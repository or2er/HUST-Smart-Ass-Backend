from core.model import llm0
from langchain.chains import LLMChain

INDEX_EXTRACTOR_TEMPLATE = """
Instructions:
Your task is extracting the table of contents from the given topic to write a document.
The topic can be a person, a place, a thing, or an event.

Example:
Topic: Ho Chi Minh
Table of contents:

"""

index_extractor = LLMChain(llm=llm0)

class Summarizer:
    def __init__(self, topic):
        self.topic = topic

    def run(self):
        pass