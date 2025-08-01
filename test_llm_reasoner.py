from agents.llm_reasoner import LLMReasoningAgent

def main():
    agent = LLMReasoningAgent()
    prompt = (
        "CVE-2025-54321 is a privilege escalation flaw in sudo. "
        "It affects Ubuntu 22.04 and Debian 11. It allows users to bypass access controls "
        "and gain root privileges. How severe is this and what would rollback complexity be?"
    )

    result = agent.run(prompt)
    print("\n[LLM Justification from DeepSeek]\n")
    print(result)

if __name__ == "__main__":
    main()
