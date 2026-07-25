import os
import requests
from typing import List, Dict, Any

def search_web_evidence(query: str, api_key: str = "") -> List[Dict[str, Any]]:
    tavily_key = api_key or os.environ.get("TAVILY_API_KEY")
    evidence_list = []
    
    if tavily_key:
        try:
            url = "https://api.tavily.com/search"
            payload = {"api_key": tavily_key, "query": query, "max_results": 2}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", []):
                    evidence_list.append({
                        "publisher": item.get("domain", "Unknown Source"),
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", "")
                    })
        except Exception:
            pass
            
    return evidence_list