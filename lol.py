from dotenv import load_dotenv
load_dotenv()

from core.model import llm0 as llm
from langchain.agents import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain.utilities import WikipediaAPIWrapper
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

# memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

@tool("DietRecommendation")
def diet_recommendation():
    """
    A diet recommendation tool that can recommend a diet plan for a user.
    """
    return "ncct"

tools = load_tools(['wikipedia'])

# llm_with_tools = llm.bind(
#     functions=[format_tool_to_openai_function(t) for t in tools]
# )

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant"),
#     ("user", "{input}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad"),
# ])

# agent = {
#     "input": lambda x: x["input"],
#     "agent_scratchpad": lambda x: format_to_openai_functions(x['intermediate_steps'])
# } | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser()

# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# agent_executor.invoke({ "input": 'who is donald trump' })
agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

agent.run("who is donald trump")