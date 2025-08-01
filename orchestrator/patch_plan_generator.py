from agents.patch_planner import PatchPlannerAgent
from agents.rag_retriever import RAGRetrieverAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.llm_reasoner import LLMReasoningAgent


class PatchPlanGenerator:
    def __init__(self, use_llm=False):
        self.planner = PatchPlannerAgent(
            cve_file_path="backend/data/mock_cves.json",
            vendor_notes_dir="backend/data/vendor_notes"
        )
        self.rag = RAGRetrieverAgent(vendor_notes_dir="backend/data/vendor_notes")
        self.use_llm = use_llm
        self.llm_reasoner = LLMReasoningAgent() if use_llm else None
        self.assessor = RiskAssessorAgent(use_llm=use_llm, llm_reasoner=self.llm_reasoner)

    def generate_patch_plan(self):
        print("[PatchPlanGenerator] Step 1: Get raw CVEs and vendor notes")
        patch_inputs = self.planner.run()

        print("[PatchPlanGenerator] Step 2: Index vendor notes in Chroma")
        self.rag.ingest_documents()

        print("[PatchPlanGenerator] Step 3: Assess risk with LLM explanations")
        patch_risks = self.assessor.assess_all(patch_inputs["cves"])

        # Attach RAG results (optional)
        vendor_summary = self.rag.query("Summarize all vendor patch priorities")

        return {
            "patch_risks": patch_risks,
            "vendor_summary": vendor_summary
        }
