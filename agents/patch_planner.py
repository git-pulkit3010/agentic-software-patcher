# backend/agents/patch_planner.py

import json
from pathlib import Path

class PatchPlannerAgent:
    def __init__(self, cve_file_path: str, vendor_notes_dir: str, policy_keywords: list = None):
        self.cve_file_path = Path(cve_file_path)
        self.vendor_notes_dir = Path(vendor_notes_dir)
        self.policy_keywords = policy_keywords or ["critical", "high", "reboot", "network"]

    def fetch_latest_cves(self):
        if not self.cve_file_path.exists():
            raise FileNotFoundError("CVE file not found.")
        
        with open(self.cve_file_path, "r") as f:
            cve_data = json.load(f)
        return cve_data

    def fetch_vendor_notes(self):
        notes = []
        for file in self.vendor_notes_dir.glob("*.txt"):
            with open(file, "r") as f:
                content = f.read()
                notes.append({
                    "vendor": file.stem,
                    "content": content
                })
        return notes

    def extract_relevant_policy_terms(self, notes):
        extracted = []
        for note in notes:
            matches = [kw for kw in self.policy_keywords if kw in note["content"].lower()]
            extracted.append({
                "vendor": note["vendor"],
                "matched_keywords": matches,
                "full_note": note["content"]
            })
        return extracted

    def run(self):
        print("[PatchPlannerAgent] Fetching latest CVEs...")
        cves = self.fetch_latest_cves()

        print("[PatchPlannerAgent] Reading vendor patch notes...")
        vendor_notes = self.fetch_vendor_notes()

        print("[PatchPlannerAgent] Extracting relevant policy keywords...")
        policies = self.extract_relevant_policy_terms(vendor_notes)

        return {
            "cves": cves,
            "vendor_policies": policies
        }
