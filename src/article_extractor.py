import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 15


# ============================================================
# EXTRACT URL FROM HTML
# ============================================================

def extract_original_url(html):
    """
    Try to find the original publisher URL
    from a Google News page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # --------------------------------------------------------
    # 1. Canonical URL
    # --------------------------------------------------------

    canonical = soup.find(
        "link",
        rel="canonical"
    )

    if canonical:

        url = canonical.get("href", "").strip()

        if is_valid_external_url(url):
            return url

    # --------------------------------------------------------
    # 2. OpenGraph URL
    # --------------------------------------------------------

    og_url = soup.find(
        "meta",
        property="og:url"
    )

    if og_url:

        url = og_url.get("content", "").strip()

        if is_valid_external_url(url):
            return url

    # --------------------------------------------------------
    # 3. Search HTML for external URLs
    # --------------------------------------------------------

    urls = re.findall(
        r'https?://[^\s"\'<>]+',
        html
    )

    for url in urls:

        url = url.rstrip(
            '.,;:)\'"'
        )

        if is_valid_external_url(url):
            return url

    return None


# ============================================================
# CHECK WHETHER URL IS AN EXTERNAL PUBLISHER URL
# ============================================================

def is_valid_external_url(url):
    """
    Return True if the URL appears to belong
    to an external publisher rather than Google.
    """

    if not url:
        return False

    try:

        parsed = urlparse(url)

        if parsed.scheme not in (
            "http",
            "https"
        ):
            return False

        domain = parsed.netloc.lower()

        # Ignore Google domains
        google_domains = [
            "google.com",
            "google.co.in",
            "news.google.com",
            "googleusercontent.com",
            "gstatic.com"
        ]

        for google_domain in google_domains:

            if (
                domain == google_domain
                or domain.endswith(
                    "." + google_domain
                )
            ):
                return False

        return True

    except Exception:

        return False


# ============================================================
# RESOLVE GOOGLE NEWS URL
# ============================================================

def resolve_google_news_url(
    google_url
):
    """
    Attempt to resolve a Google News URL
    to the original publisher URL.
    """

    try:

        response = requests.get(
            google_url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        print(
            f"Status code: {response.status_code}"
        )

        print(
            f"Final URL: {response.url}"
        )

        # ----------------------------------------------------
        # Method 1:
        # HTTP redirect
        # ----------------------------------------------------

        if is_valid_external_url(
            response.url
        ):

            return response.url

        # ----------------------------------------------------
        # Method 2:
        # Look inside page HTML
        # ----------------------------------------------------

        original_url = extract_original_url(
            response.text
        )

        if original_url:
            return original_url

        return None

    except requests.RequestException as e:

        print(
            "Request error:",
            e
        )

        return None


# ============================================================
# EXTRACT ARTICLE TEXT
# ============================================================

def extract_article_text(
    article_url
):
    """
    Download an article page and extract
    readable article text.
    """

    try:

        response = requests.get(
            article_url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:

            print(
                f"Article request failed: "
                f"{response.status_code}"
            )

            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # ----------------------------------------------------
        # Remove unnecessary elements
        # ----------------------------------------------------

        for element in soup(
            [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "form",
                "noscript"
            ]
        ):

            element.decompose()

        # ----------------------------------------------------
        # Try article tag first
        # ----------------------------------------------------

        article = soup.find(
            "article"
        )

        if article:

            paragraphs = article.find_all(
                "p"
            )

        else:

            paragraphs = soup.find_all(
                "p"
            )

        # ----------------------------------------------------
        # Extract paragraphs
        # ----------------------------------------------------

        text_parts = []

        for paragraph in paragraphs:

            text = paragraph.get_text(
                " ",
                strip=True
            )

            text = re.sub(
                r"\s+",
                " ",
                text
            )

            if len(text) >= 40:

                text_parts.append(
                    text
                )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        unique_parts = []

        seen = set()

        for text in text_parts:

            normalized = text.lower()

            if normalized not in seen:

                seen.add(
                    normalized
                )

                unique_parts.append(
                    text
                )

        # ----------------------------------------------------
        # Combine article
        # ----------------------------------------------------

        article_text = "\n\n".join(
            unique_parts
        )

        if len(article_text) < 200:

            return None

        return article_text

    except requests.RequestException as e:

        print(
            "Article extraction error:",
            e
        )

        return None

    except Exception as e:

        print(
            "Unexpected extraction error:",
            e
        )

        return None


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    google_url = input(
        "\nPaste a Google News article link: "
    ).strip()

    if not google_url:

        print(
            "\nPlease enter a Google News URL."
        )

        raise SystemExit

    print(
        "\nResolving original article..."
    )

    original_url = resolve_google_news_url(
        google_url
    )

    print(
        "\n" + "=" * 70
    )

    if not original_url:

        print(
            "Could not find the original article URL."
        )

        print(
            "\nGoogle News did not expose the "
            "publisher URL directly."
        )

        raise SystemExit

    print(
        "ORIGINAL ARTICLE URL"
    )

    print(
        "=" * 70
    )

    print(
        original_url
    )

    # --------------------------------------------------------
    # Extract article
    # --------------------------------------------------------

    print(
        "\nExtracting article text..."
    )

    article_text = extract_article_text(
        original_url
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "EXTRACTED ARTICLE"
    )

    print(
        "=" * 70
    )

    if article_text:

        print(
            article_text
        )

        print(
            "\n" + "=" * 70
        )

        print(
            f"Characters extracted: "
            f"{len(article_text)}"
        )

    else:

        print(
            "Could not extract article text."
        )