# ============================================================
# FACTCHECK AI - FACT CHECKER
# ============================================================

import re
from collections import Counter


# ============================================================
# 1. TEXT CLEANING
# ============================================================

def normalize_text(text):
    """
    Convert text to a normalized form for comparison.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 2. GET IMPORTANT WORDS
# ============================================================

def get_keywords(text):
    """
    Extract useful words from a sentence.

    Common English words are ignored.
    """

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "to",
        "of",
        "in",
        "on",
        "at",
        "for",
        "from",
        "with",
        "and",
        "or",
        "but",
        "that",
        "this",
        "it",
        "as",
        "by",
        "has",
        "have",
        "had",
        "will",
        "would",
        "can",
        "could",
        "may",
        "might",
        "about",
        "into",
        "than",
        "after",
        "before",
        "during",
        "its",
        "their",
        "they",
        "he",
        "she",
        "we",
        "you",
        "according",
        "reported",
        "reports",
        "said",
        "says"
    }

    words = normalize_text(text).split()

    keywords = [
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    ]

    return keywords


# ============================================================
# 3. FACT MATCHING
# ============================================================

def calculate_fact_match(claim, evidence):
    """
    Calculate how closely the evidence matches
    the important words in the claim.

    Returns a value between 0 and 1.
    """

    claim_words = get_keywords(claim)
    evidence_words = get_keywords(evidence)

    if not claim_words:
        return 0.0

    if not evidence_words:
        return 0.0

    claim_counter = Counter(claim_words)
    evidence_counter = Counter(evidence_words)

    matched_words = 0

    for word in claim_counter:

        if word in evidence_counter:

            matched_words += min(
                claim_counter[word],
                evidence_counter[word]
            )

    score = matched_words / len(claim_words)

    return min(score, 1.0)


# ============================================================
# 4. CLASSIFY EVIDENCE
# ============================================================

def classify_evidence(
    nli_label,
    nli_score,
    fact_match
):
    """
    Combine NLI classification and fact matching.

    Returns:

        {
            "category": "support",
            "combined_score": 0.82
        }
    """

    nli_label = (
        nli_label
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # Entailment
    # --------------------------------------------------------

    if nli_label == "entailment":

        combined_score = (
            0.70 * nli_score
            +
            0.30 * fact_match
        )

        # If NLI strongly supports the claim,
        # classify it as supporting evidence.
        if nli_score >= 0.55:

            return {
                "category": "support",
                "combined_score": combined_score
            }

        return {
            "category": "neutral",
            "combined_score": combined_score
        }

    # --------------------------------------------------------
    # Contradiction
    # --------------------------------------------------------

    if nli_label == "contradiction":

        combined_score = (
            0.70 * nli_score
            +
            0.30 * fact_match
        )

        # If NLI strongly contradicts the claim,
        # classify it as contradicting evidence.
        if nli_score >= 0.55:

            return {
                "category": "contradiction",
                "combined_score": combined_score
            }

        return {
            "category": "neutral",
            "combined_score": combined_score
        }

    # --------------------------------------------------------
    # Neutral
    # --------------------------------------------------------

    combined_score = (
        0.70 * nli_score
        +
        0.30 * fact_match
    )

    return {
        "category": "neutral",
        "combined_score": combined_score
    }


# ============================================================
# 5. SOURCE QUALITY
# ============================================================

def get_source_quality(source):
    """
    Assign a basic source-quality score.

    Returns a value between 0 and 1.
    """

    if not source:
        return 0.30

    source_lower = (
        source
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # High-quality / trusted news sources
    # --------------------------------------------------------

    high_quality_sources = [

        "reuters",

        "associated press",

        "ap news",

        "bbc",

        "the hindu",

        "the indian express",

        "press information bureau",

        "pib",

        "ndtv",

        "times of india",

        "hindustan times",

        "the times of india",

        "deccan herald",

        "economic times",

        "financial times",

        "pti",

        "press trust of india",

        "the new indian express",

        "india today",

        "news18",

        "business standard",

        "moneycontrol",

        "livemint"

    ]

    for trusted_source in high_quality_sources:

        if trusted_source in source_lower:

            return 0.90


    # --------------------------------------------------------
    # Government / institutional sources
    # --------------------------------------------------------

    government_sources = [

        "government",

        "gov.in",

        "ministry",

        "reserve bank",

        "rbi",

        "niti aayog",

        "world bank",

        "united nations",

        "un.org",

        "who",

        "isro"

    ]

    for trusted_source in government_sources:

        if trusted_source in source_lower:

            return 0.95


    # --------------------------------------------------------
    # Other recognizable news sources
    # --------------------------------------------------------

    general_news_sources = [

        "the week",

        "the wire",

        "the quint",

        "firstpost",

        "scroll",

        "the print",

        "deccan herald",

        "outlook",

        "financial express",

        "business today",

        "zee news",

        "times now",

        "india tv",

        "dna"

    ]

    for news_source in general_news_sources:

        if news_source in source_lower:

            return 0.75


    # --------------------------------------------------------
    # Unknown source
    # --------------------------------------------------------

    return 0.50


# ============================================================
# 6. COMBINE ALL EVIDENCE SIGNALS
# ============================================================

def calculate_combined_score(
    nli_score,
    fact_match,
    source_quality
):
    """
    Combine:

        NLI confidence
        Fact matching
        Source quality

    into one evidence score.
    """

    combined_score = (

        0.60 * nli_score

        +

        0.25 * fact_match

        +

        0.15 * source_quality

    )

    return min(
        max(
            combined_score,
            0.0
        ),
        1.0
    )


# ============================================================
# 7. PROCESS SINGLE EVIDENCE
# ============================================================

def process_evidence(
    claim,
    article,
    nli_label,
    nli_score
):
    """
    Process one news article and return
    all evidence signals together.
    """

    headline = article.get(
        "headline",
        ""
    )

    evidence = article.get(
        "evidence",
        ""
    )

    source = article.get(
        "source",
        "Unknown"
    )

    # --------------------------------------------------------
    # Combine headline and article evidence
    # --------------------------------------------------------

    evidence_text = (
        headline
        + ". "
        + evidence
    )

    # --------------------------------------------------------
    # Calculate fact matching
    # --------------------------------------------------------

    fact_match = calculate_fact_match(
        claim,
        evidence_text
    )

    # --------------------------------------------------------
    # Calculate source quality
    # --------------------------------------------------------

    source_quality = get_source_quality(
        source
    )

    # --------------------------------------------------------
    # Classify evidence
    # --------------------------------------------------------

    classification = classify_evidence(
        nli_label,
        nli_score,
        fact_match
    )

    # --------------------------------------------------------
    # Calculate final evidence score
    # --------------------------------------------------------

    combined_score = calculate_combined_score(
        nli_score,
        fact_match,
        source_quality
    )

    # --------------------------------------------------------
    # Return complete result
    # --------------------------------------------------------

    return {

        "label": nli_label,

        "nli_score": nli_score,

        "category": classification[
            "category"
        ],

        "fact_match": fact_match,

        "source_quality": source_quality,

        "combined_score": combined_score,

        "article": article

    }


# ============================================================
# 8. TEST
# ============================================================

if __name__ == "__main__":

    test_claim = (
        "India's GDP grew by 7.8 percent "
        "in the latest quarter."
    )

    test_article = {

        "headline":
            "India GDP growth reaches 7.8 percent "
            "in latest quarter",

        "source":
            "Reuters",

        "evidence":
            "India's economy recorded strong "
            "GDP growth during the latest quarter.",

        "published":
            "Unknown",

        "link":
            ""

    }

    result = process_evidence(

        claim=test_claim,

        article=test_article,

        nli_label="entailment",

        nli_score=0.92

    )

    print(
        "\n" + "=" * 60
    )

    print(
        "FACT CHECKER TEST"
    )

    print(
        "=" * 60
    )

    print(
        f"\nCategory: "
        f"{result['category']}"
    )

    print(
        f"NLI Score: "
        f"{result['nli_score']:.3f}"
    )

    print(
        f"Fact Match: "
        f"{result['fact_match']:.3f}"
    )

    print(
        f"Source Quality: "
        f"{result['source_quality']:.3f}"
    )

    print(
        f"Combined Score: "
        f"{result['combined_score']:.3f}"
    )