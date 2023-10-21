import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import VertexAIEmbeddings
import tiktoken

tokenize = tiktoken.get_encoding('cl100k_base')

def create_llm(model, temperature):
    llm = ChatOpenAI(
        temperature=temperature,
        model=model,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
        model_kwargs={
            "headers": { "HTTP-Referer": "https://github.com" },
        }
    )
    return llm

def tiktoken_len(text):
    tokens = tokenize.encode(text, disallowed_special=())
    return len(tokens)

llm = create_llm('gpt-3.5-turbo', 0.8)
llm0 = create_llm('gpt-3.5-turbo', 0)
# llm0 = create_llm('gpt-4', 0)

embeddings = VertexAIEmbeddings()

