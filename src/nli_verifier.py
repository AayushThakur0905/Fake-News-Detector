from transformers import pipeline
import torch

from src.news_search import search_news


# ============================================================
# 1. DEVICE SETUP
# ============================================================

if torch.cuda.is_available():
    device = 0
    print("GPU detected:", torch.cuda.get_device_name(0))
else:
    device = -1
    print("GPU not available. Using CPU.")


# ============================================================
# 2. LOAD NLI MODEL
# ============================================================

print("\nLoading NLI model...")

classifier = pipeline(
    "text-classification",
    model="facebook/bart-large-mnli",
    device=device
)

print("NLI model loaded successfully.")


# ============================================================
# 3. NLI ANALYSIS
# ============================================================

def analyze_evidence(claim, evidence):
    """
    Compare evidence against the claim using
    BART-MNLI.

    Premise:
        Evidence from the news article

    Hypothesis:
        User's claim
    """

    try:

        # IMPORTANT:
        # Pass premise and hypothesis separately.
        result = classifier(
            evidence,
            text_pair=claim
        )

        label = result[0]["label"].lower()

        score = float(
            result[0]["score"]
        )

        return {

            "label": label,

            "score": score

        }

    except Exception as e:

        print(
            "\nNLI analysis error:",
            str(e)
        )

        return {

            "label": "neutral",

            "score": 0.0

        }


# ============================================================
# 4. ANALYZE CLAIM
# ============================================================

def analyze_claim(claim):
    """
    Search news sources (with relevance filtering) and
    perform NLI analysis on each relevant source.
    """

    results = search_news(
        claim
    )

    analyzed_results = []


    # --------------------------------------------------------
    # Analyze every relevant article
    # --------------------------------------------------------

    for article in results:

        # Combine headline and article evidence
        evidence_text = (
            article["headline"]
            + ". "
            + article["evidence"]
        )


        # ----------------------------------------------------
        # NLI
        # ----------------------------------------------------

        nli_result = analyze_evidence(
            claim,
            evidence_text
        )


        # ----------------------------------------------------
        # Store complete result
        # ----------------------------------------------------

        analyzed_results.append({

            "headline":
                article["headline"],

            "source":
                article["source"],

            "published":
                article["published"],

            "evidence":
                article["evidence"],

            "link":
                article["link"],

            "search_query":
                article.get("search_query", ""),

            "similarity":
                article.get("similarity", 0.0),

            "label":
                nli_result["label"],

            "score":
                nli_result["score"]

        })


    return analyzed_results


# ============================================================
# 5. TEST
# ============================================================

if __name__ == "__main__":

    claim = input(
        "\nEnter a news claim to verify: "
    )


    if not claim.strip():

        print(
            "\nPlease enter a claim."
        )


    else:

        print(
            "\nSearching for evidence..."
        )


        results = analyze_claim(
            claim
        )


        if not results:

            print(
                "\nNo relevant news results found."
            )


        else:

            print(
                "\nAnalyzing evidence with NLI..."
            )

            print(
                "\n" + "=" * 70
            )

            print(
                "NEWS EVIDENCE ANALYSIS"
            )

            print(
                "=" * 70
            )


            for i, result in enumerate(
                results,
                start=1
            ):

                print(
                    "\n" + "-" * 70
                )

                print(
                    f"[{i}/{len(results)}]"
                )

                print(
                    f"NLI: "
                    f"{result['label'].upper()} "
                    f"({result['score']:.3f})"
                )

                print(
                    f"Relevance: "
                    f"{result['similarity']:.3f}"
                )

                print(
                    f"Source: "
                    f"{result['source']}"
                )

                print(
                    f"Published: "
                    f"{result['published']}"
                )

                print(
                    f"Evidence: "
                    f"{result['evidence']}"
                )

                print(
                    f"Link: "
                    f"{result['link']}"
                )