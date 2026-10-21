from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.nli_verifier import analyze_claim
from src.verdict_engine import calculate_verdict


# ============================================================
# 1. CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="FactCheck AI API",
    description="AI-powered news claim verification API",
    version="1.0.0"
)


# ============================================================
# 2. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. REQUEST MODEL
# ============================================================

class ClaimRequest(BaseModel):

    claim: str


# ============================================================
# 4. HEALTH CHECK
# ============================================================

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "FactCheck AI API is running"
    }


# ============================================================
# 5. FACT CHECK ENDPOINT
# ============================================================

@app.post("/fact-check")
def fact_check(request: ClaimRequest):

    claim = request.claim.strip()

    # --------------------------------------------------------
    # Validate claim
    # --------------------------------------------------------

    if not claim:

        return {
            "success": False,
            "error": "Please enter a claim."
        }

    print("\n" + "=" * 70)

    print(
        "FACT CHECK REQUEST"
    )

    print("=" * 70)

    print(
        f"\nClaim: {claim}"
    )


    # --------------------------------------------------------
    # Search news + NLI
    # --------------------------------------------------------

    print(
        "\nSearching Google News..."
    )

    analyzed_results = analyze_claim(
        claim
    )

    print(
        f"\nFound {len(analyzed_results)} results."
    )


    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not analyzed_results:

        return {
            "success": True,

            "claim": claim,

            "verdict": {
                "verdict": "INSUFFICIENT EVIDENCE",
                "confidence": 0.0,
                "support": 0,
                "contradiction": 0,
                "neutral": 0,
                "weighted_support": 0.0,
                "weighted_contradiction": 0.0,
                "weighted_neutral": 0.0
            },

            "sources": []
        }


    # --------------------------------------------------------
    # Prepare NLI results for verdict engine
    # --------------------------------------------------------

    nli_results = []

    for article in analyzed_results:

        nli_results.append({

            "label": article["label"],

            "score": article["score"]

        })


    # --------------------------------------------------------
    # DEBUG — temporary, remove once diagnosed
    # --------------------------------------------------------

    print(
        "\nDEBUG — entailment scores: "
        f"{[r['score'] for r in nli_results if r['label'] == 'entailment']}"
    )

    print(
        "DEBUG — contradiction scores: "
        f"{[r['score'] for r in nli_results if r['label'] == 'contradiction']}"
    )


    # --------------------------------------------------------
    # Calculate verdict
    # --------------------------------------------------------

    print(
        "\nCalculating final verdict..."
    )

    verdict = calculate_verdict(
        nli_results
    )


    # --------------------------------------------------------
    # Print result
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL FACT CHECK"
    )

    print(
        "=" * 70
    )

    print(
        f"\nClaim: {claim}"
    )

    print(
        f"\nVerdict: "
        f"{verdict['verdict']}"
    )

    print(
        f"Evidence Confidence: "
        f"{verdict['confidence'] * 100:.1f}%"
    )

    print(
        f"\nSupporting Evidence: "
        f"{verdict['support']}"
    )

    print(
        f"Contradicting Evidence: "
        f"{verdict['contradiction']}"
    )

    print(
        f"Neutral Evidence: "
        f"{verdict['neutral']}"
    )


    # --------------------------------------------------------
    # Return API response
    # --------------------------------------------------------

    return {

        "success": True,

        "claim": claim,

        "verdict": verdict,

        "sources": analyzed_results

    }