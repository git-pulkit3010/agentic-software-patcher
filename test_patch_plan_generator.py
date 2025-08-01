from orchestrator.patch_plan_generator import PatchPlanGenerator

def main():
    generator = PatchPlanGenerator(use_llm=True)
    result = generator.generate_patch_plan()

    print("\n[📌 FINAL PATCH PLAN]")
    for patch in result["patch_risks"]:
        print(f"\n🔧 {patch['cve_id']} - Risk: {patch['risk_score']}")
        print(f"  Severity: {patch['severity']}")
        print(f"  Dependency Risk: {patch['dependency_risk']}")
        print(f"  Rollback Difficulty: {patch['rollback_difficulty']}")
        if patch["llm_reasoning"]:
            print(f"  💬 LLM Justification:\n{patch['llm_reasoning']}")

    print("\n📢 Vendor Summary (RAG):\n")
    print(result["vendor_summary"])

if __name__ == "__main__":
    main()
