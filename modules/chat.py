from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryMemory,ChatMessageHistory
from langchain.chat_models import ChatOpenAI

from .knowledge_graph import save_context_to_graph

CHAT_TEMPLATE = """You are a personal AI assistant. Your name is THT
Don't justify your answers.
Don't preface your answer with "As an AI assistant...".

Context:
{context}

History:
{history}

Human: {prompt}
AI:"""

CHAT_PROMPT = PromptTemplate.from_template(CHAT_TEMPLATE)

llm = ChatOpenAI(temperature=0.8)

chat_history = ChatMessageHistory()

chat_memory = ConversationSummaryMemory(
  llm=ChatOpenAI(temperature=0),
  chat_memory=chat_history
)

chat_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{prompt}"))

def chat(user_input):
    response = chat_chain(CHAT_PROMPT.format(prompt=user_input, history=chat_memory.buffer, context=""))

    output = response['text']

    chat_history.add_user_message(user_input)
    chat_history.add_ai_message(output)
    chat_memory.buffer = chat_memory.predict_new_summary(chat_history.messages, chat_memory.buffer)

    save_context_to_graph(user_input, output, chat_memory.buffer)

    return output
