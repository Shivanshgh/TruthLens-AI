import streamlit as st
import os
import nltk
nltk.download("punkt_tab")
nltk.download("punkt")
nltk.download("vader_lexicon")
from src.ml_classifier import predict_ml
from src.red_flags import detect_red_flags
from src.claim_extractor import extract_claims_with_llm
from src.evidence_retriever import search_web_evidence
from src.llm_analyzer import analyze_with_llm
from src.scoring import compute_credibility_score

def main():
    st.set_page_config(page_title="TruthLens - AI Misinformation Analyzer", page_icon="🛡️", layout="wide")
    
    st.title("🛡️ TruthLens: AI Misinformation & Credibility Intelligence")
    st.markdown("An evidence-aware intelligence system combining Machine Learning, linguistic risk signals, real web evidence retrieval, and structured LLM reasoning.")

    
    st.sidebar.header("🔑 API & Model Config")
    
    selected_option = st.sidebar.selectbox("LLM Provider", ["None", "gemini (Free Tier)"])
    llm_provider = "gemini" if "gemini" in selected_option else "None"
    
    api_key_input = st.sidebar.text_input("Gemini API Key (Optional if secret set)", type="password")
    search_api_key = st.sidebar.text_input("Tavily Search API Key", type="password")
    
    st.sidebar.info("Tip: Set environment variables or secrets for deployment convenience.")

    samples = [
        "Select a sample...",
        "BREAKING: Secret cure for aging discovered by local mom, doctors hate her!",
        "The Federal Reserve announced a quarter-point interest rate cut on Wednesday."
    ]
    selected_sample = st.selectbox("Load Sample Text", samples)
    default_text = selected_sample if selected_sample != "Select a sample..." else ""
    
    user_input = st.text_area("Paste news article or text snippet:", value=default_text, height=140)

    if st.button("Run Comprehensive Credibility Analysis", type="primary"):
        if not user_input.strip():
            st.warning("Please enter text to analyze.")
            return

        with st.spinner("Running multilayer credibility analysis..."):
            ml_res = predict_ml(user_input)
            ml_score = ml_res["reliable_probability"] * 100

        red_flags = detect_red_flags(user_input)


        if red_flags is None:
            
            red_flags = []
        elif not isinstance(red_flags, list):
            red_flags = list(red_flags)

        linguistic_score = max(0, 100 - (len(red_flags) * 25))

         claims = extract_claims_with_llm(user_input, provider=llm_provider, api_key=api_key_input)

            all_evidence = []
            for c in claims[:2]:
                results = search_web_evidence(c["claim"], api_key=search_api_key)
                all_evidence.extend(results)

            llm_res = {}
            if llm_provider != "None":
                llm_res = analyze_with_llm(user_input, claims, all_evidence, provider=llm_provider, api_key=api_key_input)
            
            llm_score = llm_res.get("factual_grounding_score", 0.5) * 100
            
            if all_evidence:
                evidence_score = 75.0 if llm_res.get("overall_assessment") == "supported" else 40.0
                source_quality = 70.0
            else:
                evidence_score = 50.0
                source_quality = 50.0

            scoring_result = compute_credibility_score(evidence_score, source_quality, ml_score, linguistic_score, llm_score)

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Credibility Score", f"{scoring_result['score']}/100", scoring_result['risk_level'])
        with col2:
            st.metric("ML Classification", ml_res["prediction"].upper(), f"Confidence: {ml_res['confidence']:.2%}")
        with col3:
            st.metric("Linguistic Risk Signals", len(red_flags))

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Score Breakdown", "🚨 Linguistic Signals", "📝 Claim Analysis", "🌐 Evidence Sources", "🧠 LLM Deep-Dive"])

        with tab1:
            st.subheader("Transparent Composite Score Breakdown")
            st.write("Formula: `30% Evidence + 25% Source Quality + 20% ML + 15% Linguistic + 10% LLM`")
            for k, v in scoring_result["breakdown"].items():
                st.progress(int(v), text=f"{k}: {v}/100")

        with tab2:
            st.subheader("Linguistic Risk Signals (Warning Indicators)")
            if red_flags:
                for rf in red_flags:
                    st.warning(f"**{rf['flag']}** ({rf['severity'].upper()} severity)\n\n*Evidence:* `{rf['evidence']}`\n\n*Explanation:* {rf['explanation']}")
            else:
                st.success("No linguistic red flags detected.")

        with tab3:
            st.subheader("Extracted Core Claims")
            if claims:
                for idx, clm in enumerate(claims, 1):
                    st.info(f"**Claim {idx}:** {clm.get('claim')} \n\n*Type:* {clm.get('type')}")
            else:
                st.write("No distinct factual claims extracted.")

        with tab4:
            st.subheader("Retrieved Web Evidence")
            if all_evidence:
                for ev in all_evidence:
                    st.markdown(f"**Publisher:** {ev['publisher']}\n\n**Title:** [{ev['title']}]({ev['url']})\n\n> {ev['snippet']}")
                    st.divider()
            else:
                st.info("No external web search results retrieved. (Provide a Tavily API key for live verification).")

        with tab5:
            st.subheader("Structured LLM Intelligence Assessment")
            if llm_provider == "None":
                st.info("Select an LLM provider in the sidebar to enable cognitive evaluation.")
            else:
                st.json(llm_res)

if __name__ == "__main__":
    main()
