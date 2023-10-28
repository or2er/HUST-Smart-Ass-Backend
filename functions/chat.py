from langchain.utilities import WikipediaAPIWrapper
from langchain.tools.python.tool import PythonREPLTool
from langchain.agents import Tool, AgentType, tool
from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from pydantic import BaseModel, Field

from .article_generator import ArticleGenerator
from .recommendation import Person

from core.model import llm0
from functions.neo4j import graph_chain
from datetime import datetime
from typing import Type, Optional, List

import pickle

wikipedia = WikipediaAPIWrapper()
search = DuckDuckGoSearchRun()
repl_tool = PythonREPLTool()

@tool("Memory")
def personal_storage(message: str):
    """
    A memory tool that can store user typical information and retrieve it later.
    Examples: "I love math", "Linda is a teacher", "My password is 1234"
    """
    
    result = graph_chain(message)['result']

    if result is None or len(result) == 0:
        return message
    
    return result

@tool
def diet_recommendation():
    """
    A diet recommendation tool that can recommend a diet plan for a user.
    """
    
    meals_calories_perc = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.25}
    plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
    losses = [1, 0.9, 0.8, 0.6]
    weight_plan = 'Maintain weight'
    weight_loss = losses[plans.index(weight_plan)]
    person = Person(age=18,
                    height=175.0,
                    weight=75.0,
                    gender='Male',
                    activity='Moderate exercise (3-5 days/wk)',
                    meals_calories_perc=meals_calories_perc,
                    weight_loss=weight_loss)
    
    output = person.generate_recommendations()
    meals = {k: [ t['RecipeIngredientParts'] for t in v] for k, v in output.items() if k in ['breakfast', 'lunch', 'dinner']}

    return meals

class BrowserInput(BaseModel):
    topic: str = Field(description="The name of the topic to summarize")

class BrowserTool(BaseTool):
    name = 'Browser'
    description = 'Add a bot to the background queue to browse the web and summarize the topic'
    args_schema: Type[BrowserInput] = BrowserInput

    def _run(self, topic: str):
        generator = ArticleGenerator(topic)

        def execute():
            from server import append_docu_task
            from functions.document import DocumentAbout
            output_article = generator.run()
            append_docu_task(DocumentAbout({
                "id": generator.id,
                "type": "topic",
                "name": topic,
                "processing_status": 0
            }))
            with open(f"data/{generator.id}.pkl", 'wb') as fp:
                pickle.dump(output_article, fp)
            from wsevent import update_progress
            update_progress(generator.id, 1)
        
        from server import tasks
        tasks.put(execute)

        return f"{generator.id}||Activity found! The bot is now browsing the web and generating the article about {topic}. You can check the progress in the auto-function tab."

wikipedia_tool = Tool(
    name='Wikipedia',
    func= wikipedia.run,
    description="useful when you need an answer about encyclopedic general knowledge"
)

duckduckgo_tool = Tool(
    name='Search',
    func= search.run,
    description="useful for when you need to answer questions about current events. You should ask targeted questions"
)

tools = [repl_tool, wikipedia_tool, duckduckgo_tool, BrowserTool(), diet_recommendation]

memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

llm_with_tools = llm0.bind(
    functions=[format_tool_to_openai_function(t) for t in tools]
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_openai_functions(x['intermediate_steps'])
} | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser()

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

knowledge_graph_agent = personal_storage

def extract_yt_url(message: str):
    import re
    try:
        fir = re.search("(?P<url>youtu?[^\s]+)", message).group("url")
        if fir.find("/watch?v=") != -1:
            return fir.split("/watch?v=")[1].split("&")[0]
        else:
            return fir.split(".be/")[1].split("&")[0]
    except Exception as e:
        return None

def chat(message: str, knowledge_graph: bool):
    extract_id = extract_yt_url(message)
    if extract_id != None:
        from server import create_docu_task
        from functions.yt_processing import yt_transcript
        data = yt_transcript(extract_id)
        create_docu_task(data)
        return {
            "msg": f"Activity found! I'm currently processing YouTube video: {data.get('name')}. Track progress and interact with this video in Auto-function tab.",
            "type": "yt",
            "data": f"yt_{extract_id}"
        }
    try:
        if knowledge_graph:
            return {
                "msg": knowledge_graph_agent(message),
                "type": "knowledge_graph",
                "data": ""
            }
        else:
            message += " (current time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
            output = str(agent_executor.invoke({ 'input': message })).split("||")
            if len(output) > 1:
                return {
                    "msg": output[1],
                    "type": "topic" if output[1].startswith("Activity found!") else "normal",
                    "data": output[0] if output[1].startswith("Activity found!") else "",
                }
            else:
                return {
                    "msg": output[0],
                    "type": "normal",
                    "data": ""
                }
    except Exception as e:
        response = str(e)

        if not response.startswith("Could not parse LLM output: "):
            # return {
            #     "msg": "There was an error while processing your request. Please try again later.",
            #     "type": "normal",
            #     "data": ""
            # }
            raise e
        response = response.removeprefix("Could not parse LLM output: ").removesuffix("")

        return {
            "msg": response,
            "type": "normal",
            "data": ""
        }
