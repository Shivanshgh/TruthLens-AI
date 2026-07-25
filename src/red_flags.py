from typing import List, Dict, Any

def detect_red_flags(text: str) -> List[Dict[str, Any]]:
    flags = []
    lower_text = text.lower()
    
    sensational_terms = ["shocking", "secret", "miracle", "doctors hate", "mind-blowing", "unbelievable"]
    for term in sensational_terms:
        if term in lower_text:
            flags.append({
                "flag": "Sensationalist Language",
                "severity": "medium",
                "evidence": term,
                "explanation": "Uses emotionally charged buzzwords designed to manipulate reader attention."
            })
            break

    if sum(1 for c in text if c.isupper()) / max(1, len(text)) > 0.3 and len(text) > 15:
        flags.append({
            "flag": "Excessive Capitalization",
            "severity": "low",
            "evidence": text[:40] + "...",
            "explanation": "High capitalization indicates emotional urgency or shouting."
        })

    if text.count("!") > 2 or text.count("?") > 2:
        flags.append({
            "flag": "Excessive Punctuation",
            "severity": "low",
            "evidence": f"Exclamation count: {text.count('!')}, Question count: {text.count('?')}",
            "explanation": "Punctuation abuse is a common marker of clickbait or ragebait."
        })

    absolute_terms = ["cure all", "instantly", "melt 30lbs", "100% effective", "guaranteed"]
    for term in absolute_terms:
        if term in lower_text:
            flags.append({
                "flag": "Absolute/Miracle Claims",
                "severity": "high",
                "evidence": term,
                "explanation": "Makes sweeping, scientifically improbable or unfalsifiable promises."
            })
            break

    urgency_terms = ["urgent", "share before deleted", "forward this", "they don't want you to know"]
    for term in urgency_terms:
        if term in lower_text:
            flags.append({
                "flag": "Urgency & Conspiracy Framing",
                "severity": "high",
                "evidence": term,
                "explanation": "Employs pressure tactics and conspiracy tropes to bypass critical thinking."
            })
            break

    return flags