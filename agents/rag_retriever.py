# backend/agents/rag_retriever.py

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

load_dotenv()

# Load DeepSeek key (OpenAI compatible format)
os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"

CHROMA_PATH = "backend/rag_store/chromadb"

class RAGRetrieverAgent:
    def __init__(self, vendor_notes_dir: str):
        self.vendor_notes_dir = Path(vendor_notes_dir)
        self.vectorstore = None

    def ingest_documents(self):
        print("[RAGRetrieverAgent] Ingesting vendor notes...")

        all_docs = []
        found_files = list(self.vendor_notes_dir.rglob("*.txt"))

        if not found_files:
            raise FileNotFoundError("No vendor notes found under the specified directory.")

        for file_path in found_files:
            print(f"  - Found file: {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
                print(f"    Contents:\n{content[:150]}...\n")

            loader = TextLoader(str(file_path))
            docs = loader.load()
            all_docs.extend(docs)

        splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        chunks = splitter.split_documents(all_docs)

        valid_chunks = [chunk for chunk in chunks if chunk.page_content.strip() != ""]

        if not valid_chunks:
            raise ValueError("No valid content chunks found to embed.")

        print(f"[RAGRetrieverAgent] Preparing {len(valid_chunks)} chunks for embedding...")

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma.from_documents(valid_chunks, embeddings, persist_directory=CHROMA_PATH)
        self.vectorstore.persist()

        print(f"[RAGRetrieverAgent] Ingested {len(valid_chunks)} valid chunks.")
        return len(valid_chunks)




    def query(self, question: str, top_k=3):
        if not self.vectorstore:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.get_relevant_documents(question)

        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = PromptTemplate.from_template(
            "You are a patch planning assistant. Based on the following vendor context:\n\n{context}\n\nAnswer this: {question}"
        )

        chain = RunnableLambda(lambda inputs: self._llm_call(prompt.format(**inputs)))
        response = chain.invoke({"context": context, "question": question})
        return response

    def _llm_call(self, full_prompt: str):
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful software patching analyst."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
