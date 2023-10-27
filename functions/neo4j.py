import os
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.prompts import PromptTemplate
from core.model import llm, llm0

CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to modify and query a graph database.
Instructions:
User name is "Minh".
He studies Cyber Security at Hanoi University of Science and Technology (HUST).
Use the provided relationship types and properties in the schema.
You can use new relationships and properties if needed.
Only use MERGE query or modify the graph.
Use MERGE with only property "name".
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

Example:
Linda is 1.2 meters tall.
MERGE (linda:Person {{name: "Linda"}})
SET linda.height = 1.2;

Where do Linda live?
MERGE (linda:Person {{name: "Linda"}})
RETURN linda;

Schema:
{schema}

The question is:
{question}"""

graph = Neo4jGraph(
    url=os.environ['NEO4J_URL'],
    username=os.environ['NEO4J_USERNAME'], 
    password=os.environ['NEO4J_PASSWORD']
)

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

graph_chain = GraphCypherQAChain.from_llm(
    llm0, graph=graph, verbose=True, cypher_prompt=CYPHER_GENERATION_PROMPT
)