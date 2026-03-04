import json
from services.llm_extractor import call_llm, clean_json_response
from error_handler import InvalidJSONError


def extract_company_list(search_results: list) -> list:
    prompt = f"""
From the search results below,
extract up to 5 company names relevant to the query.

Return ONLY valid JSON:

{{
  "companies": ["Company A", "Company B"]
}}

Search results:
{json.dumps(search_results, indent=2)}
"""

    content = call_llm(prompt)
    content = clean_json_response(content)

    try:
        parsed = json.loads(content)
        return parsed.get("companies", [])
    except json.JSONDecodeError as e:
        raise InvalidJSONError(f"Company discovery returned invalid JSON: {e}")