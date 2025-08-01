from agents.rag_retriever import RAGRetrieverAgent

def main():
    agent = RAGRetrieverAgent(vendor_notes_dir="backend/data/vendor_notes")
    agent.ingest_documents()
    result = agent.query("What are the most critical patch actions from vendor notes?")
    print("\n[DeepSeek LLM RESPONSE]\n")
    print(result)

if __name__ == "__main__":
    main()
