import json
import os
from typing import List, Dict, Any
from google import genai

def extract_claims_with_llm(text: str, provider: str = "gemini", api_key: str = "") -> List[Dict[str, Any]]:
    # If provider is None, skip right to fallback
    if provider == "None":
        sentences = [s.strip() for s in text.split('.') if len(s.split()) > 5]
        return [{"claim": s, "type": "general", "requires_verification": True} for s in sentences[:3]]

    prompt = f"""
    Analyze the following text and extract up to 4 core verifiable factual claims. 
    Ignore opinions, questions, or subjective emotional statements.
    
    Return ONLY a JSON object with this exact schema:
    {{
      "claims": [
        {{
          "claim": "Specific factual claim extracted.",
          "type": "economic | political | health | scientific | general",
          "requires_verification": true
        }}
      ]
    }}
    
    Text: "{text}"
    """
    
    try:
        client = genai.Client(api_key=api_key if api_key else os.environ.get("GEMINI_API_KEY"))
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text).get("claims", [])
    except Exception:
        pass
        
    sentences = [s.strip() for s in text.split('.') if len(s.split()) > 5]
    return [{"claim": s, "type": "general", "requires_verification": True} for s in sentences[:3]]