
import streamlit as st

from src.nli_verifier import analyze_claim
from src.verdict_engine import calculate_verdict


st.set_page_config(
    page_title="FactCheck AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 FactCheck AI")
st.write("AI-powered news claim verification using news sources and evidence analysis.")

claim = st.text_area(
    "Enter a news claim",
    placeholder="Example: India is a country in Asia.",
    height=120
)

if st.button("Verify Claim", type="primary"):
    claim = claim.strip()

    if not claim:
        st.warning("Please enter a claim first.")
    else:
        try:
            with st.spinner("Searching news sources and analyzing evidence..."):
                analyzed_results = analyze_claim(claim)

                if not analyzed_results:
                    verdict = {
                        "verdict": "INSUFFICIENT EVIDENCE",
                        "confidence": 0.0,
                        "support": 0,
                        "contradiction": 0,
                        "neutral": 0,
                    }
                else:
                    nli_results = [
                        {
                            "label": article["label"],
                            "score": article["score"],
                        }
                        for article in analyzed_results
                    ]
                    verdict = calculate_verdict(nli_results)

            st.subheader("Fact-check result")
            st.write("**Claim:**", claim)

            verdict_name = verdict.get(
                "verdict", "INSUFFICIENT EVIDENCE"
            )
            st.header(verdict_name)

            confidence = verdict.get("confidence", 0.0)
            st.metric("Evidence confidence", f"{confidence * 100:.1f}%")

            col1, col2, col3 = st.columns(3)
            col1.metric("Supporting", verdict.get("support", 0))
            col2.metric("Contradicting", verdict.get("contradiction", 0))
            col3.metric("Neutral", verdict.get("neutral", 0))

            st.subheader("Sources reviewed")
            st.write(f"{len(analyzed_results)} sources found.")

            if analyzed_results:
                for i, article in enumerate(analyzed_results, start=1):
                    with st.expander(
                        f"{i}. {article.get('headline', 'News source')}"
                    ):
                        st.write(
                            "**Source:**",
                            article.get("source", "Unknown")
                        )
                        st.write(
                            "**Evidence classification:**",
                            article.get("label", "Unknown")
                        )
                        st.write(
                            article.get(
                                "evidence",
                                article.get("explanation", "No additional evidence.")
                            )
                        )

                        link = article.get("link")
                        if link:
                            st.markdown(f"[Read source]({link})")
            else:
                st.info("No matching sources were found.")

        except Exception as e:
            st.error(f"Fact-check failed: {e}")
            st.exception(e)
