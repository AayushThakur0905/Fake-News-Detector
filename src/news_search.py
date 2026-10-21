import feedparser
from urllib.parse import quote
from bs4 import BeautifulSoup
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. CLEAN HTML
# ============================================================

def clean_text(html_text):
    """
    Remove HTML tags and extra whitespace.
    """

    soup = BeautifulSoup(
        html_text,
        "html.parser"
    )

    return soup.get_text(
        " ",
        strip=True
    )


# ============================================================
# 2. NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Normalize text for relevance comparison.
    """

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
# 3. EXTRACT IMPORTANT KEYWORDS
# ============================================================

def extract_keywords(text):
    """
    Extract meaningful keywords from the claim.
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
        "has",
        "have",
        "had",
        "do",
        "does",
        "did",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "from",
        "with",
        "by",
        "and",
        "or",
        "but",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "as",
        "than",
        "into",
        "about",
        "according"
    }

    words = normalize_text(text).split()

    keywords = [
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    ]

    return set(keywords)


# ============================================================
# 4. TF-IDF SIMILARITY
# ============================================================

def calculate_similarity(claim, evidence):
    """
    Calculate TF-IDF similarity between the claim
    and evidence.
    """

    documents = [
        claim,
        evidence
    ]

    try:

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )

        tfidf_matrix = vectorizer.fit_transform(
            documents
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return float(similarity)

    except Exception:

        return 0.0


# ============================================================
# 5. KEYWORD OVERLAP
# ============================================================

def calculate_keyword_overlap(claim, evidence):
    """
    Calculate how many important claim keywords
    appear in the evidence.
    """

    claim_keywords = extract_keywords(
        claim
    )

    evidence_keywords = extract_keywords(
        evidence
    )

    if not claim_keywords:
        return 0.0

    common_keywords = (
        claim_keywords
        & evidence_keywords
    )

    return (
        len(common_keywords)
        / len(claim_keywords)
    )


# ============================================================
# 6. PHRASE MATCH
# ============================================================

def calculate_phrase_match(claim, evidence):
    """
    Give extra relevance to exact or strong phrases
    from the claim.
    """

    claim_normalized = normalize_text(
        claim
    )

    evidence_normalized = normalize_text(
        evidence
    )

    # Full claim appears in evidence
    if (
        len(claim_normalized) > 10
        and claim_normalized in evidence_normalized
    ):
        return 1.0

    # Check meaningful 3-word phrases
    claim_words = claim_normalized.split()

    if len(claim_words) < 3:
        return 0.0

    phrase_matches = 0
    total_phrases = 0

    for i in range(
        len(claim_words) - 2
    ):

        phrase = " ".join(
            claim_words[i:i + 3]
        )

        total_phrases += 1

        if phrase in evidence_normalized:
            phrase_matches += 1

    if total_phrases == 0:
        return 0.0

    return (
        phrase_matches
        / total_phrases
    )


# ============================================================
# 7. FINAL RELEVANCE SCORE
# ============================================================

def calculate_relevance(
    claim,
    evidence
):
    """
    Combine multiple relevance signals.

    TF-IDF:
        Measures textual similarity.

    Keyword overlap:
        Measures important claim terms
        appearing in evidence.

    Phrase match:
        Rewards strong phrase matches.
    """

    similarity = calculate_similarity(
        claim,
        evidence
    )

    keyword_overlap = calculate_keyword_overlap(
        claim,
        evidence
    )

    phrase_match = calculate_phrase_match(
        claim,
        evidence
    )

    # Weighted relevance score
    relevance = (
        similarity * 0.40
        + keyword_overlap * 0.40
        + phrase_match * 0.20
    )

    return float(relevance)


# ============================================================
# 8. BUILD SEARCH QUERIES
# ============================================================

def build_search_queries(claim):
    """
    Create several search variations.

    This helps Google News find evidence when the
    exact wording of the claim does not appear
    in an article.
    """

    queries = []

    # Original claim
    queries.append(
        claim
    )

    # Exact claim
    queries.append(
        f'"{claim}"'
    )

    # Important keywords
    keywords = extract_keywords(
        claim
    )

    if keywords:

        keyword_query = " ".join(
            keywords
        )

        queries.append(
            keyword_query
        )

    # Keep order while removing duplicates
    unique_queries = []

    for query in queries:

        if (
            query.strip()
            and query not in unique_queries
        ):
            unique_queries.append(
                query
            )

    return unique_queries


# ============================================================
# 9. SEARCH GOOGLE NEWS
# ============================================================

def search_google_news(query):
    """
    Search Google News RSS for one query.
    """

    encoded_query = quote(
        query
    )

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    try:

        feed = feedparser.parse(
            url
        )

    except Exception:

        return []

    results = []

    for article in feed.entries[:20]:

        title = article.get(
            "title",
            "No title available"
        )

        # ----------------------------------------------------
        # Separate headline and source
        # ----------------------------------------------------

        if " - " in title:

            headline, source = title.rsplit(
                " - ",
                1
            )

        else:

            headline = title
            source = "Unknown"

        # ----------------------------------------------------
        # Publication date
        # ----------------------------------------------------

        published = article.get(
            "published",
            "Publication date unavailable"
        )

        # ----------------------------------------------------
        # Article summary
        # ----------------------------------------------------

        raw_summary = article.get(
            "summary",
            ""
        )

        summary = clean_text(
            raw_summary
        )

        if len(summary) > 500:

            summary = (
                summary[:500]
                + "..."
            )

        # ----------------------------------------------------
        # Combined evidence
        # ----------------------------------------------------

        evidence_text = (
            headline
            + ". "
            + summary
        )

        results.append({

            "headline": headline,

            "source": source,

            "published": published,

            "evidence": summary,

            "link": article.get(
                "link",
                ""
            ),

            "search_query": query,

            "evidence_text": evidence_text

        })

    return results


# ============================================================
# 10. SEARCH MULTIPLE QUERY VARIATIONS
# ============================================================

def search_news(query):
    """
    Search Google News using multiple query variations,
    remove duplicates, calculate relevance, and return
    the strongest evidence.
    """

    search_queries = build_search_queries(
        query
    )

    all_candidates = []

    # --------------------------------------------------------
    # Search each query variation
    # --------------------------------------------------------

    for search_query in search_queries:

        results = search_google_news(
            search_query
        )

        all_candidates.extend(
            results
        )

    # --------------------------------------------------------
    # Remove duplicate articles
    # --------------------------------------------------------

    unique_articles = {}

    for article in all_candidates:

        link = article.get(
            "link",
            ""
        )

        headline = article.get(
            "headline",
            ""
        )

        # Prefer link as unique identifier
        # and headline as fallback.
        identifier = (
            link
            if link
            else normalize_text(
                headline
            )
        )

        if identifier not in unique_articles:

            unique_articles[
                identifier
            ] = article

    candidates = list(
        unique_articles.values()
    )

    # --------------------------------------------------------
    # Calculate relevance
    # --------------------------------------------------------

    for article in candidates:

        evidence_text = article[
            "evidence_text"
        ]

        relevance = calculate_relevance(
            query,
            evidence_text
        )

        article[
            "similarity"
        ] = relevance

    # --------------------------------------------------------
    # Sort strongest evidence first
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: x[
            "similarity"
        ],
        reverse=True
    )

    # --------------------------------------------------------
    # Keep relevant evidence
    # --------------------------------------------------------

    relevant_results = [
        article
        for article in candidates
        if article[
            "similarity"
        ] >= 0.12
    ]

    # --------------------------------------------------------
    # Return maximum 10 sources
    # --------------------------------------------------------

    return relevant_results[:10]


# ============================================================
# 11. TEST
# ============================================================

if __name__ == "__main__":

    claim = input(
        "\nEnter a news claim to verify: "
    )

    if not claim.strip():

        print(
            "\nPlease enter a news claim."
        )

    else:

        print(
            "\nSearching for evidence..."
        )

        results = search_news(
            claim
        )

        print(
            "\n" + "=" * 70
        )

        print(
            "NEWS VERIFICATION SEARCH"
        )

        print(
            "=" * 70
        )

        print(
            f"\nClaim: {claim}"
        )

        if not results:

            print(
                "\nNo sufficiently relevant "
                "results found."
            )

        else:

            print(
                f"\nFound {len(results)} "
                "relevant sources."
            )

            for i, article in enumerate(
                results,
                start=1
            ):

                print(
                    "\n" + "-" * 70
                )

                print(
                    f"RESULT #{i}"
                )

                print(
                    "-" * 70
                )

                print(
                    f"Headline: "
                    f"{article['headline']}"
                )

                print(
                    f"Source: "
                    f"{article['source']}"
                )

                print(
                    f"Published: "
                    f"{article['published']}"
                )

                print(
                    f"Relevance: "
                    f"{article['similarity']:.3f}"
                )

                print(
                    f"Search query: "
                    f"{article['search_query']}"
                )

                print(
                    "\nEvidence:"
                )

                print(
                    article["evidence"]
                )

                print(
                    "\nLink:"
                )

                print(
                    article["link"]
                )