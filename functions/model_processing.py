import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from core.model import tiktoken_len, embeddings, llm

class ModelProcessing:
    def __init__(self, data):
        self.id = data.get("id")
        self.text = data.get("text") or ""
        self.source = data.get("source") or "query"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=tiktoken_len
        )
        self.chain = load_qa_chain(llm=llm, chain_type="stuff")
        self.status = None
    
    def process(self):
        if self.source == "query":
            if os.path.exists(f"data/vs_{self.id}"):
                self.faiss_db = FAISS.load_local(f"data/vs_{self.id}", embeddings)
                print("Loaded saved vector store")
            else:
                self.status = "Can't find saved vector store"
        else:
            if os.path.exists(f"data/vs_{self.id}"):
                self.status = "This has been processed before"
            else:
                chunks = self.text_splitter.split_text(text=self.text)
                print("Total chunks:", len(chunks))
                self.faiss_db = FAISS.from_texts(chunks, embeddings)
                self.faiss_db.save_local(f"data/vs_{self.id}")
                print("Saved newly generated vector store")

    def query(self, text):
        if self.status == None:
            similar_docs = self.faiss_db.similarity_search(query=text, k=3)
            return self.chain.run(input_documents=similar_docs, question=text)
        else:
            print(self.status)
            return self.status