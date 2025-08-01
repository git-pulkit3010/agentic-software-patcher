# backend/agents/llm_reasoner.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMReasoningAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-chat"

    def run(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity patch analyst. Assess the risk level and urgency based on the technical description provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM Error]: {str(e)}"
