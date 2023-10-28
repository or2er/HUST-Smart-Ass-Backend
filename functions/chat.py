from langchain.utilities import WikipediaAPIWrapper
from langchain.tools.python.tool import PythonREPLTool
from langchain.agents import Tool, AgentType, tool
from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import MessagesPlaceholder, StringPromptTemplate
from pydantic import BaseModel, Field

from .article_generator import ArticleGenerator

from core.model import llm
from functions.neo4j import graph_chain
from datetime import datetime
from typing import Type, Optional, List

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

class BrowserInput(BaseModel):
    topic: str = Field(description="The name of the topic to summarize")

class BrowserTool(BaseTool):
    name = 'Browser'
    description = 'Add a bot to the background queue to browse the web and summarize the topic'
    args_schema: Type[BrowserInput] = BrowserInput

    def _run(self, topic: str):
        generator = ArticleGenerator(topic)

        # TODO: add generator to the background queue

        return "The bot is now browsing the web and generating the article. You can check the progress in the auto-function tab."

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

tools = [repl_tool, wikipedia_tool, duckduckgo_tool, BrowserTool()]

memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

normal_agent = initialize_agent(
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=5,
    memory=memory,
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
)

knowledge_graph_agent = initialize_agent(
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=[personal_storage],
    llm=llm,
    verbose=True,
    max_iterations=5,
    memory=memory,
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
)

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
        create_docu_task(yt_transcript(extract_id))
        return {
            "msg": f"Activity found! I'm currently processing YouTube video id {extract_id}. Track progress and interact with this video in Auto-function tab.",
            "type": "yt",
            "data": f"yt_{extract_id}"
        }
    try:
        agent = knowledge_graph_agent if knowledge_graph else normal_agent
        message += " (current time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
        return {
            "msg": agent.run(message),
            "type": "normal",
            "data": ""
        }
    except Exception as e:
        response = str(e)

        if not response.startswith("Could not parse LLM output: "):
            return {
                "msg": "There was an error while processing your request. Please try again later.",
                "type": "normal",
                "data": ""
            }
        
        response = response.removeprefix("Could not parse LLM output: ").removesuffix("")

        return {
            "msg": response,
            "type": "normal",
            "data": ""
        }
