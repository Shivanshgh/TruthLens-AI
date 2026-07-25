import json
import os
from typing import Dict, Any, List
from google import genai

def analyze_with_llm(text: str, claims: List[dict], evidence_data: List[dict], provider: str = "gemini", api_key: str = "") -> Dict[str, Any]:
    default_response = {
        "overall_assessment": "unverified",
        "factual_grounding_score": 0.5,
        "reasoning": "LLM evaluation unavailable or failed to parse response.",
        "confidence": "low",
        "logical_fallacies": [],
        "claim_evaluations": []
    }

    if provider == "None":
        return default_response

    prompt = f"""
    You are an expert intelligence analyst specializing in misinformation assessment.
    Analyze the text against the retrieved external evidence.
    
    Text: "{text}"
    Extracted Claims: {json.dumps(claims)}
    Retrieved Evidence: {json.dumps(evidence_data)}
    
    Evaluate thoroughly and return ONLY a valid JSON object matching this schema:
    {{
      "overall_assessment": "supported | partially_supported | contradicted | unverified",
      "factual_grounding_score": 0.0 to 1.0,
      "reasoning": "Comprehensive explanation of how evidence supports, contradicts, or leaves claims unverified.",
      "confidence": "low | medium | high",
      "logical_fallacies": ["list any logical fallacies found"],
      "claim_evaluations": [
        {{
          "claim": "string",
          "verdict": "supported | contradicted | unverified",
          "explanation": "string"
        }}
      ]
    }}
    """

    try:
        client = genai.Client(api_key=api_key if api_key else os.environ.get("GEMINI_API_KEY"))
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception:
        pass
        
    return default_response