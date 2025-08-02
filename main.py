# backend/main.py - Enhanced for Phase 3

from orchestrator.patch_plan_generator import PatchPlanGenerator
from agents.human_approval_agent import HumanApprovalAgent
from agents.explainer_agent import ExplainerAgent
from agents.audit_logger_agent import AuditLoggerAgent
import json
import requests

def main():
    print("=== Agentic Patch Management System - Phase 3 Demo ===\n")

    # Initialize the patch plan generator with LLM support
    generator = PatchPlanGenerator(use_llm=True)
    
    # Initialize Phase 3 agents
    approval_agent = HumanApprovalAgent()
    explainer_agent = ExplainerAgent()
    audit_logger = AuditLoggerAgent()

    try:
        # Generate the complete patch plan (Phase 1 + Phase 2)
        print("[Phase 1 & 2] Generating patch plan with LLM assistance...")
        patch_plan = generator.generate_patch_plan()

        # Display results
        print("\n=== PATCH PLAN GENERATED ===")
        print(f"Audit ID: {patch_plan.get('audit_id', 'N/A')}")
        print(f"Total Scheduled Patches: {len(patch_plan.get('scheduled_patches', []))}")
        print(f"Compliance Frameworks: {patch_plan.get('plan_metadata', {}).get('compliance_summary', {}).get('frameworks_involved', [])}")
        print(f"Documentation Required: {patch_plan.get('plan_metadata', {}).get('compliance_summary', {}).get('patches_requiring_documentation', 0)} patches")

        # Show first scheduled patch example
        if patch_plan.get('scheduled_patches'):
            first_patch = patch_plan['scheduled_patches'][0]
            print(f"\nExample Scheduled Patch:")
            print(f" CVE: {first_patch.get('cve_id', 'N/A')}")
            print(f" Target System: {first_patch.get('target_system', {}).get('name', 'N/A')}")
            print(f" Scheduled Time: {first_patch.get('scheduled_time', 'N/A')}")
            print(f" Risk Score: {first_patch.get('risk_score', 'N/A')}")
            print(f" Compliance Frameworks: {first_patch.get('compliance_metadata', {}).get('applicable_frameworks', [])}")

        # Phase 3: Create approval request
        print("\n=== PHASE 3: Human Approval Process ===")
        print("[Phase 3] Creating approval request...")
        approval_id = approval_agent.create_approval_request(
            patch_plan=patch_plan,
            requester="phase3_demo"
        )
        
        print(f"✅ Approval request created: {approval_id}")
        
        # Generate explanations
        print("[Phase 3] Generating LLM explanations...")
        explanations = explainer_agent.generate_patch_plan_summary(patch_plan)
        
        print("📋 Generated explanations:")
        for explanation_type, content in explanations.items():
            print(f" - {explanation_type.replace('_', ' ').title()}: {len(content)} characters")
        
        # Save complete plan to file for inspection
        output_file = "backend/data/complete_patch_plan_phase3.json"
        with open(output_file, "w") as f:
            # Add Phase 3 data to the patch plan
            enhanced_patch_plan = {
                **patch_plan,
                "phase3_data": {
                    "approval_id": approval_id,
                    "explanations": explanations,
                    "phase3_status": "approval_pending"
                }
            }
            json.dump(enhanced_patch_plan, f, indent=2)

        print(f"\n💾 Complete Phase 3 patch plan saved to: {output_file}")

        # Send to API server (if running)
        try:
            print("[Phase 3] Sending to API server...")
            resp = requests.post(
                "http://127.0.0.1:8000/patch-plan",
                json={"patch_plan": patch_plan},
                timeout=10
            )
            print(f"📡 API Response: {resp.status_code}")
            if resp.status_code == 200:
                response_data = resp.json()
                print(f"   Server approval ID: {response_data.get('approval_id', 'N/A')}")
            else:
                print(f"   Error: {resp.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  API server not accessible: {e}")
            print("   Start the server with: python api_server.py")

        # Display Phase 3 summary
        print("\n=== PHASE 3 SUMMARY ===")
        print("✅ Patch plan generated with LLM assistance")
        print("✅ Approval request created for human review")
        print("✅ Comprehensive explanations generated")
        print("✅ Audit trail established")
        print("\n🎯 Next Steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Start the React frontend: cd frontend && npm start")
        print("3. Review and approve patches in the web interface")
        print(f"4. Check approval request: {approval_id}")

    except Exception as e:
        print(f"❌ Error in Phase 3 demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()