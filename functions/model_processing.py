import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from core.model import tiktoken_len, embeddings, llm
from wsevent import update_progress

class ModelProcessing:
    def print_debug(self, msg):
        print(f"[id={self.id}] {msg}.")

    def __init__(self, data):
        self.id = data.get("id")
        self.text = data.get("text") or ""
        self.type = data.get("type") or "query"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=300,
            length_function=tiktoken_len
        )
        self.chain = load_qa_chain(llm=llm, chain_type="stuff")
        self.status = None
        self.processing_status = 0
        self.print_debug("New model created")

    def process(self):
        if self.id == None:
            self.status = "Where is the id??"
            self.print_debug(self.status)
            return
        
        if self.type == "query":
            if os.path.exists(f"data/vs_{self.id}"):
                self.faiss_db = FAISS.load_local(f"data/vs_{self.id}", embeddings)
                self.processing_status = 1
                self.print_debug("Loaded previous DB")
            else:
                self.status = "Can't find saved DB."
        else:
            if os.path.exists(f"data/vs_{self.id}"):
                self.status = None
                self.faiss_db = FAISS.load_local(f"data/vs_{self.id}", embeddings)
                self.processing_status = 1
                self.print_debug("Loaded previous DB")
            elif self.text == None or self.text == "":
                self.status = "Where text??"
            else:
                self.status = "Processing, please wait"
                self.print_debug("Processing")

                chunks = self.text_splitter.split_text(text=self.text)
                self.print_debug(f"Num of chunks: {len(chunks)}")

                for i, chunk in enumerate(chunks):
                    temp_db = FAISS.from_texts(chunk, embeddings)
                    self.faiss_db.merge_from(temp_db)
                    
                    self.processing_status = (i+1)/len(chunk)
                    self.print_debug(f"Processed {i+1}/{len(chunks)}, percentage: {format((i+1)/len(chunks)*100, '.2f')}%")
                    update_progress(self.id, (i+1)/len(chunk))
                
                self.status = None
                self.processing_status = 1
                self.faiss_db.save_local(f"data/vs_{self.id}")
                self.print_debug("Saved DB.")

    def query(self, text):
        if self.status == None and self.processing_status == 1:
            similar_docs = self.faiss_db.similarity_search(query=text, k=3)
            return self.chain.run(input_documents=similar_docs, question=text)
        else:
            self.print_debug(self.status)
            return self.status