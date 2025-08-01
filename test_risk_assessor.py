from agents.risk_assessor import RiskAssessorAgent
import json

def load_mock_cves():
    with open("backend/data/mock_cves.json", "r") as f:
        return json.load(f)

def main():
    cves = load_mock_cves()
    assessor = RiskAssessorAgent()
    results = assessor.assess_all(cves)

    print("\n[Patch Risk Scores]")
    for result in results:
        print(f"  - {result['cve_id']}: Risk = {result['risk_score']} "
              f"(Severity: {result['severity']}, Dependency: {result['dependency_risk']}, "
              f"Rollback: {result['rollback_difficulty']})")

if __name__ == "__main__":
    main()
