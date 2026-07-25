def compute_credibility_score(
    evidence_score: float,   # 0 - 100
    source_quality: float,   # 0 - 100
    ml_score: float,         # 0 - 100
    linguistic_score: float, # 0 - 100
    llm_score: float         # 0 - 100
) -> dict:
    final_score = (
        0.30 * evidence_score +
        0.25 * source_quality +
        0.20 * ml_score +
        0.15 * linguistic_score +
        0.10 * llm_score
    )
    
    score_val = max(0, min(100, int(final_score)))
    
    if score_val >= 75:
        risk_level = "Low Risk (Likely Credible)"
    elif score_val >= 45:
        risk_level = "Medium Risk (Unverified / Mixed)"
    else:
        risk_level = "High Risk (Potentially Misleading)"
        
    return {
        "score": score_val,
        "risk_level": risk_level,
        "breakdown": {
            "Evidence Verification": round(evidence_score, 1),
            "Source Quality": round(source_quality, 1),
            "ML Analysis": round(ml_score, 1),
            "Linguistic Signals": round(linguistic_score, 1),
            "LLM Analysis": round(llm_score, 1)
        }
    }