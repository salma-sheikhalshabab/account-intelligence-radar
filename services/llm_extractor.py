import json
import re
import requests
from config import settings
from error_handler import LLMError, LLMInsufficientBalanceError, InvalidJSONError


# ==============================
# Prompt Builder
# ==============================

def build_extraction_prompt(company_name: str, markdown_content: str, objective: str) -> str:
    return f"""
You are a business intelligence extraction engine.

Company: {company_name}

Objective:
{objective}

Rules:
- Use ONLY the provided content.
- Extract only factual information.
- Every fact MUST include its source URL.
- Return ONLY valid JSON.
- Do NOT include explanations or commentary.
- Structure the JSON dynamically based on the objective.
- Use meaningful keys.

CONTENT:
{markdown_content[:12000]}
"""


# ==============================
# JSON Cleaner
# ==============================

def clean_json_response(content: str) -> str:
    content = re.sub(r"```json", "", content)
    content = re.sub(r"```", "", content)

    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        content = content[start:end + 1]

    return content.strip()


# ==============================
# Shared LLM Call
# ==============================

def call_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Account Intelligence Radar"
    }

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(settings.OPENROUTER_URL, headers=headers, json=payload, timeout=30)

    if response.status_code == 402:
        raise LLMInsufficientBalanceError("Insufficient balance — HTTP 402.")

    if response.status_code != 200:
        raise LLMError(f"LLM API Error {response.status_code}: {response.text}")

    data = response.json()

    if "choices" not in data:
        raise LLMError(f"Unexpected LLM response structure: {data}")

    return data["choices"][0]["message"]["content"]


# ==============================
# Main Extraction Function
# ==============================

def extract_structured_json(company_name: str, markdown_content: str, objective: str) -> dict:
    prompt = build_extraction_prompt(company_name, markdown_content, objective)

    content = call_llm(prompt)
    cleaned = clean_json_response(content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise InvalidJSONError(f"Could not parse LLM response as JSON: {e}\nRaw: {cleaned[:300]}")