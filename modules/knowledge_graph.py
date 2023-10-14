import re

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings

from .neo4j import graph

EXTRACT_TEMPLATE = """Given a prompt from a chat between human and AI, extrapolate as many relationships as possible from it.
Instructions:
The relationship is directed, so the order is very important.
Return 'empty' if no relationships are found.
You are not allowed to extrapolate relationships from history.
Ouput format: entity1,relationship,entity2 or entity,property1:value1,...

It is recommended to use the following relationships: {relationships}

Example:
history: This is Alice.
prompt: she is my roommate. she is pretty. she is 20 years old. I am her boyfriend.
output:
Alice,is_roommate_of,human
human,is_boyfriend_of,Alice
Alice,age:20,appearance:pretty

history: {history}
prompt: {sentence}
output:
"""

EXTRACT_PROMPT = PromptTemplate.from_template(EXTRACT_TEMPLATE)

extract_chain = LLMChain(llm=ChatOpenAI(temperature=0),prompt=PromptTemplate.from_template("{prompt}"))

embeddings = OpenAIEmbeddings()

def parse_extract_output(output):
    results = {
        "relationships": [],
        "entities": {},
    }

    if output.strip() == 'empty':
        return results

    for line in output.split("\n"):
        if line == "":
            continue
        items = line.split(",")

        if len(items) < 2:
            continue

        if ':' in items[1]:
            entity = items[0]
            data = {}
            for item in items[1:]:
                [key, value] = item.split(":")
                data[key] = value
            results["entities"][entity] = data
        else:
            results["relationships"].append(items)
            
    return results

def format_name(name):
    pattern = r'[!@#$%^&*()\-=_+\[\]{}|;:\'",.<>?/\\]'
    return re.sub(pattern, '_', name)

def save_context_to_graph(user_input, ai_output, history):
    context = user_input + "\n" + ai_output
    context_embedding =  embeddings.embed_documents([context])[0]
    print("Finish embedding")

    relationships = graph.query("""
        CALL apoc.meta.data()
        YIELD label, elementType, type, property
        WHERE type = "RELATIONSHIP" AND elementType = "node"
        RETURN property
    """)

    relationships = [relationship['property'] for relationship in relationships]
    relationships = ",".join(relationships)

    extract_output = extract_chain(EXTRACT_PROMPT.format(sentence=user_input, history=history, relationships=relationships))['text']
    print(extract_output)
    
    entities = set()

    results = parse_extract_output(extract_output)

    for triplet in results["relationships"]:
        entities.add(triplet[0])
        entities.add(triplet[2])

    for name in results["entities"].keys():
        entities.add(name)
        
    CREATE_ENTITIES_QUERY = ""
    CREATE_RELATIONSHIPS_QUERY = ""

    for entity in entities:
        data = { "name": entity }
        name = format_name(entity)

        if entity in results["entities"]:
            data = { **data, **results["entities"][entity] }

        data_str = "{"
        for key in data.keys():
            data_str += "{}: '{}', ".format(key, data[key])
        data_str = data_str[:-2]
        data_str += "}"

        CREATE_ENTITIES_QUERY += """
            MERGE ({}: Node {})
        """.format(name, data_str)

    for [entity1, relationship, entity2] in results["relationships"]:
        entity1 = format_name(entity1)
        entity2 = format_name(entity2)

        CREATE_RELATIONSHIPS_QUERY += """
           MERGE ({})-[:{}]->({})
           MERGE (context)-[:RELATE_TO]->({})
        """.format(entity1, relationship.upper(), entity2, entity1)

    graph.query("""
        CREATE (context: Context {{ text: "{}", embedding: {} }})
        {}
        {}
        RETURN context;
    """.format(context, context_embedding, CREATE_ENTITIES_QUERY, CREATE_RELATIONSHIPS_QUERY))
    print("Finish saving context to graph")