# reuse from previous project

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
import tiktoken

from dotenv import load_dotenv

load_dotenv()

tokenize = tiktoken.get_encoding('cl100k_base')
# llm = OpenAI(temperature=0, max_tokens=2048) # Normal LLM model
llm = ChatOpenAI(temperature=0, max_tokens=2048, model="gpt-3.5-turbo") # Chat optimized model
embeddings_model = OpenAIEmbeddings()

def tiktoken_len(text):
    tokens = tokenize.encode(text, disallowed_special=())
    return len(tokens)