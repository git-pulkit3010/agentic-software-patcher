# backend/agents/risk_assessor.py

import random
from typing import List, Dict

class RiskAssessorAgent:
    def __init__(self, use_llm=False, llm_reasoner=None):
        self.use_llm = use_llm
        self.llm_reasoner = llm_reasoner

    def score_patch(self, cve: Dict) -> Dict:
        severity = cve.get("severity", "").lower()
        base_score = {
            "critical": 90,
            "high": 75,
            "medium": 50,
            "low": 30
        }.get(severity, 10)

        # Mocked logic for extra weights
        dependency_risk = random.choice(["low", "medium", "high"])
        rollback_difficulty = random.choice(["easy", "moderate", "hard"])

        if dependency_risk == "high":
            base_score += 10
        elif dependency_risk == "medium":
            base_score += 5

        if rollback_difficulty == "hard":
            base_score += 5
        elif rollback_difficulty == "moderate":
            base_score += 2

        score = min(base_score, 100)

        llm_reasoning = ""
        if self.use_llm and self.llm_reasoner:
            prompt = (
                f"Evaluate this CVE for patch risk:\n"
                f"ID: {cve.get('id')}\n"
                f"Description: {cve.get('description')}\n"
                f"Severity: {severity}\n"
                f"Dependency Risk: {dependency_risk}\n"
                f"Rollback Difficulty: {rollback_difficulty}\n"
            )
            llm_reasoning = self.llm_reasoner.run(prompt)

        return {
            "cve_id": cve.get("id"),
            "severity": severity,
            "risk_score": score,
            "dependency_risk": dependency_risk,
            "rollback_difficulty": rollback_difficulty,
            "llm_reasoning": llm_reasoning
        }

    def assess_all(self, cves: List[Dict]) -> List[Dict]:
        return [self.score_patch(cve) for cve in cves]
