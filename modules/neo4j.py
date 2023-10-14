import os

from langchain.graphs import Neo4jGraph

graph = Neo4jGraph(
    url=os.environ['NEO4J_URL'],
    username=os.environ['NEO4J_USERNAME'], 
    password=os.environ['NEO4J_PASSWORD']
)
