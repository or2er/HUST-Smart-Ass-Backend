from dotenv import load_dotenv
load_dotenv()

from modules.chat import chat, chat_memory
from modules.neo4j import graph

from modules.knowledge_graph import embeddings

# context = "I am NInh"
# embedding = embeddings.embed_documents([context])[0]

# result = graph.query("""
#     CALL db.index.vector.queryNodes('embedding', 10, {})
#     YIELD node AS context, score
#     RETURN context, score
# """.format(embedding))

# for record in result:
#     print(record['context']['text'])
#     print(record['score'])

while True:
    user_input = input("You: ")
    output = chat(user_input)

    print("AI:", output)
    print("Memory:", chat_memory.buffer)

graph._driver.close()