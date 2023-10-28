from langchain.utilities import WikipediaAPIWrapper
from langchain.tools.python.tool import PythonREPLTool
from langchain.agents import Tool, AgentType, tool
from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import MessagesPlaceholder, StringPromptTemplate
from pydantic import BaseModel, Field

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

class SummarzerInput(BaseModel):
    topic: str = Field(description="The name of the topic to summarize")
    time: Optional[datetime] = Field(default=None, description="Time to finish the task, if not mentioned, return None, time format: YYYY-MM-DD HH:MM:SS")

class SummarizerTool(BaseTool):
    name = 'Summarizer'
    description = 'Add a summarizer to the background queue to summarize a topic. Use "Clock" to get the current time'
    args_schema: Type[SummarzerInput] = SummarzerInput

    def _run(self, topic: str, time: Optional[datetime] = None):
        # TODO: add a summarizer to the background queue
        print(topic, time)

        return "Summarizer added to the background queue, you will be notified when it's done"

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

tools = [repl_tool, wikipedia_tool, duckduckgo_tool, personal_storage, SummarizerTool()]

memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

agent = initialize_agent(
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

def chat(message: str):
    extract_id = extract_yt_url(message)
    if extract_id != None:
        from server import create_docu_task
        from functions.yt_processing import yt_transcript
        create_docu_task(yt_transcript(extract_id))
        return f"Activity found! I'm currently processing YouTube video id {extract_id}. Track progress and interact with this video in Auto-function tab."
    try:
        message += " (current time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
        return agent.run(message)
    except Exception as e:
        response = str(e)

        if not response.startswith("Could not parse LLM output: "):
            raise e
        
        response = response.removeprefix("Could not parse LLM output: ").removesuffix("")

        return response
