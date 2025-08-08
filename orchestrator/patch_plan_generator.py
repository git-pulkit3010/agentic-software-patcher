# backend/orchestrator/patch_plan_generator.py - Enhanced for Phase 3

from agents.patch_planner import PatchPlannerAgent
from agents.rag_retriever import RAGRetrieverAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.llm_reasoner import LLMReasoningAgent
from agents.patch_scheduler import PatchSchedulerAgent
from agents.auditor import AuditorAgent
# Phase 3 imports
from agents.human_approval_agent import HumanApprovalAgent
from agents.explainer_agent import ExplainerAgent
from agents.audit_logger_agent import AuditLoggerAgent
from agents.patch_executor import PatchExecutor  # Add with other imports
from datetime import datetime  # Add with other imports

class PatchPlanGenerator:
    def __init__(self, use_llm=False, deploy_mode = 'dry-run'):
        self.planner = PatchPlannerAgent(
            cve_file_path="backend/data/mock_cves.json",
            vendor_notes_dir="backend/data/vendor_notes"
        )
        self.rag = RAGRetrieverAgent(vendor_notes_dir="backend/data/vendor_notes")
        self.use_llm = use_llm
        self.llm_reasoner = LLMReasoningAgent() if use_llm else None
        self.assessor = RiskAssessorAgent(use_llm=use_llm, llm_reasoner=self.llm_reasoner)
        
        # Phase 2 agents
        self.scheduler = PatchSchedulerAgent()
        self.auditor = AuditorAgent()
        
        # Phase 3 agents
        self.approval_agent = HumanApprovalAgent()
        self.explainer_agent = ExplainerAgent()
        self.audit_logger = AuditLoggerAgent()
        self.deploy_mode = deploy_mode
        if deploy_mode == 'production':
            self.executor = PatchExecutor()  # Add this line

    def generate_patch_plan(self, create_approval_request=False):
        print("[PatchPlanGenerator] === PHASE 1: Patch Identification & Risk Assessment ===")
        print("[PatchPlanGenerator] Step 1: Get raw CVEs and vendor notes")
        patch_inputs = self.planner.run()

        print("[PatchPlanGenerator] Step 2: Index vendor notes in Chroma")
        self.rag.ingest_documents()

        print("[PatchPlanGenerator] Step 3: Assess risk with LLM explanations")
        patch_risks = self.assessor.assess_all(patch_inputs["cves"])

        # Attach RAG results (optional)
        vendor_summary = self.rag.query("Summarize all vendor patch priorities")

        print("[PatchPlanGenerator] === PHASE 2: Scheduling & Coordination ===")
        print("[PatchPlanGenerator] Step 4: Schedule patches to systems")
        scheduled_patches = self.scheduler.run(patch_risks)

        print("[PatchPlanGenerator] Step 5: Add compliance and audit metadata")
        final_patch_plan = self.auditor.run(scheduled_patches)

        # Add Phase 1 results to final plan
        final_patch_plan["vendor_summary"] = vendor_summary
        final_patch_plan["phase_1_results"] = {
            "patch_risks": patch_risks,
            "vendor_policies": patch_inputs["vendor_policies"]
        }
        
        # Phase 3: Prepare for human approval
        if create_approval_request:
            print("[PatchPlanGenerator] === PHASE 3: Human Approval Preparation ===")
            print("[PatchPlanGenerator] Step 6: Generate explanations")
            explanations = self.explainer_agent.generate_patch_plan_summary(final_patch_plan)
            
            print("[PatchPlanGenerator] Step 7: Create approval request")
            approval_id = self.approval_agent.create_approval_request(
                patch_plan=final_patch_plan,
                requester="automated_system"
            )
            
            print("[PatchPlanGenerator] Step 8: Log generation event")
            self.audit_logger.log_patch_plan_generation(final_patch_plan)
            
            # Add Phase 3 data to the plan
            final_patch_plan["phase3_data"] = {
                "approval_id": approval_id,
                "explanations": explanations,
                "phase3_status": "pending_approval"
            }

        print(f"[PatchPlanGenerator] ✅ Complete patch plan generated with {len(scheduled_patches)} scheduled patches")
        # Add this block right before the final return
        if self.deploy_mode == 'production':
            print("[PatchPlanGenerator] === DEPLOYMENT PHASE ===")
            print("[PatchPlanGenerator] Step 9: Validating pre-conditions")
            for check in final_patch_plan.get("pre_checks", []):
                result = self.executor._execute_wsl(
                    system={"credentials": {"user": "root"}},
                    command=check["command"]
                )
                if check.get("expect") and check["expect"] not in result["output"]:
                    raise ValueError(f"Pre-check failed for {check['command']}")
            
            print("[PatchPlanGenerator] Step 10: Executing patches")
            execution_report = {
                "timestamp": datetime.now().isoformat(),
                "steps": self.executor.execute(final_patch_plan),
                "system": "WSL2-Docker"
            }
            final_patch_plan["execution_report"] = execution_report
            self.audit_logger.log_patch_execution(execution_report)
            
        return final_patch_plan