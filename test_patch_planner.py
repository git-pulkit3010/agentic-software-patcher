from agents.patch_planner import PatchPlannerAgent

def main():
    planner = PatchPlannerAgent(
        cve_file_path="backend/data/mock_cves.json",
        vendor_notes_dir="backend/data/vendor_notes"
    )

    result = planner.run()

    print("\n[DEBUG OUTPUT] Patch Planner Output:\n")
    print(result)

if __name__ == "__main__":
    main()
