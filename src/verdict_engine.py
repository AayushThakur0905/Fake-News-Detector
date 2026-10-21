def calculate_verdict(results):
    """
    Calculate a preliminary verdict from NLI results.

    Each result should contain:
        label
        score
    """

    entailments = []
    contradictions = []
    neutrals = []

    for result in results:

        label = result["label"].lower()
        score = float(result["score"])

        if label == "entailment":
            entailments.append(score)

        elif label == "contradiction":
            contradictions.append(score)

        elif label == "neutral":
            neutrals.append(score)

    support_count = len(entailments)
    contradiction_count = len(contradictions)
    neutral_count = len(neutrals)

    total = len(results)

    # ---------------------------------------------------------
    # No evidence
    # ---------------------------------------------------------

    if total == 0:
        return {
            "verdict": "INSUFFICIENT EVIDENCE",
            "confidence": 0.0,
            "support": 0,
            "contradiction": 0,
            "neutral": 0
        }

    # ---------------------------------------------------------
    # Calculate average NLI confidence
    # ---------------------------------------------------------

    support_score = (
        sum(entailments) / support_count
        if support_count > 0
        else 0.0
    )

    contradiction_score = (
        sum(contradictions) / contradiction_count
        if contradiction_count > 0
        else 0.0
    )

    neutral_score = (
        sum(neutrals) / neutral_count
        if neutral_count > 0
        else 0.0
    )

    # ---------------------------------------------------------
    # Calculate weighted evidence
    #
    # IMPORTANT:
    # The support/contradiction ratio is calculated only
    # against each other, NOT diluted by neutral weight.
    # Neutral evidence means "not clearly relevant either
    # way" - it should not be able to drag down a verdict
    # that has real, uncontradicted supporting evidence
    # (or vice versa).
    # ---------------------------------------------------------

    support_weight = sum(entailments)
    contradiction_weight = sum(contradictions)

    opposing_weight = (
        support_weight
        + contradiction_weight
    )

    if opposing_weight > 0:
        support_ratio = support_weight / opposing_weight
        contradiction_ratio = contradiction_weight / opposing_weight
    else:
        support_ratio = 0.0
        contradiction_ratio = 0.0

    # ---------------------------------------------------------
    # Determine verdict
    # ---------------------------------------------------------

    if (
        support_count > contradiction_count
        and support_ratio >= 0.50
        and support_score >= 0.70
    ):
        verdict = "LIKELY SUPPORTED"

        confidence = support_score

    elif (
        contradiction_count > support_count
        and contradiction_ratio >= 0.50
        and contradiction_score >= 0.70
    ):
        verdict = "LIKELY CONTRADICTED"

        confidence = contradiction_score

    elif (
        support_count > 0
        and contradiction_count > 0
    ):
        verdict = "MIXED EVIDENCE"

        confidence = max(
            support_score,
            contradiction_score
        )

    else:
        verdict = "INSUFFICIENT EVIDENCE"

        confidence = neutral_score

    # ---------------------------------------------------------
    # Keep confidence between 0 and 1
    # ---------------------------------------------------------

    confidence = max(
        0.0,
        min(1.0, confidence)
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "support": support_count,
        "contradiction": contradiction_count,
        "neutral": neutral_count
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_results = [
        {
            "label": "entailment",
            "score": 0.95
        },
        {
            "label": "entailment",
            "score": 0.91
        },
        {
            "label": "entailment",
            "score": 0.89
        },
        {
            "label": "entailment",
            "score": 0.86
        },
        {
            "label": "entailment",
            "score": 0.92
        },
        {
            "label": "entailment",
            "score": 0.88
        },
        {
            "label": "entailment",
            "score": 0.90
        },
        {
            "label": "neutral",
            "score": 0.80
        },
        {
            "label": "neutral",
            "score": 0.75
        },
        {
            "label": "contradiction",
            "score": 0.85
        }
    ]

    result = calculate_verdict(test_results)

    print("\n" + "=" * 60)
    print("PRELIMINARY VERDICT")
    print("=" * 60)

    print(
        f"\nVerdict: {result['verdict']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence'] * 100:.1f}%"
    )

    print(
        f"\nSupporting sources: "
        f"{result['support']}"
    )

    print(
        f"Contradicting sources: "
        f"{result['contradiction']}"
    )

    print(
        f"Neutral sources: "
        f"{result['neutral']}"
    )