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

def chat(message: str):
    try:
        message += " (current time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
        return agent.run(message)
    except Exception as e:
        response = str(e)

        if not response.startswith("Could not parse LLM output: "):
            raise e
        
        response = response.removeprefix("Could not parse LLM output: ").removesuffix("")

        return response
