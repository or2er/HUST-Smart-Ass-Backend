import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from core.openai import tiktoken_len, embeddings_model, llm

class ModelProcessing:
    def __init__(self, data):
        self.id = data["id"]
        self.text = data["text"]
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=tiktoken_len
        )
        self.chain = load_qa_chain(llm=llm, chain_type="stuff")
    
    def process(self):
        if os.path.exists(f"data/vs_{self.id}.pkl"):
            with open(f"data/vs_{self.id}.pkl", "rb") as f:
                self.vector_store = pickle.load(f)
            print("Loaded saved vector store")
        else:
            chunks = self.text_splitter.split_text(text=self.text)
            print("Total chunks:", len(chunks))
            self.vector_store = FAISS.from_texts(chunks, embedding=embeddings_model)
            with open(f"data/vs_{self.id}.pkl", "wb") as f:
                pickle.dump(self.vector_store, f)
            print("Saved newly generated vector store")

    def query(self, text):
        similar_docs = self.vector_store.similarity_search(query=text, k=4)
        return self.chain.run(input_documents=similar_docs, question=text)