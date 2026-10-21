// ============================================================
// FACTCHECK AI - FRONTEND
// ============================================================

const API_URL = "http://127.0.0.1:8000";


// ============================================================
// CHECK CLAIM
// ============================================================

async function checkClaim() {

    const claimInput = document.getElementById("claimInput");
    const checkButton = document.getElementById("checkButton");
    const errorMessage = document.getElementById("errorMessage");

    const claim = claimInput.value.trim();

    if (!claim) {
        showError("Please enter a news claim first.");
        return;
    }

    hideError();
    showLoading();

    checkButton.disabled = true;

    try {

        updateLoadingText("Searching multiple news sources...");

        const response = await fetch(
            `${API_URL}/fact-check`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    claim: claim
                })
            }
        );


        // --------------------------------------------------------
        // Check HTTP response
        // --------------------------------------------------------

        if (!response.ok) {

            let errorText = `Server returned ${response.status}`;

            try {

                const errorData = await response.json();

                if (errorData.detail) {
                    errorText = errorData.detail;
                }

            } catch (e) {
                // Ignore JSON parsing error
            }

            throw new Error(errorText);
        }


        // --------------------------------------------------------
        // Read JSON
        // --------------------------------------------------------

        const data = await response.json();

        console.log("Backend response:", data);


        // --------------------------------------------------------
        // Backend error
        // --------------------------------------------------------

        if (data.success === false) {

            throw new Error(
                data.error ||
                data.message ||
                "Backend could not check this claim."
            );
        }


        // --------------------------------------------------------
        // Display result
        // --------------------------------------------------------

        updateLoadingText(
            "Preparing your fact-check..."
        );

        displayResults(data);

    }


    catch (error) {

        console.error(
            "FACT-CHECK ERROR:",
            error
        );

        showError(
            `Fact-check failed: ${error.message}`
        );
    }


    finally {

        hideLoading();

        checkButton.disabled = false;
    }
}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(data) {

    const resultSection =
        document.getElementById("resultSection");

    const verdict =
        data.verdict || {};

    const sources =
        data.sources || [];


    // --------------------------------------------------------
    // Claim
    // --------------------------------------------------------

    const resultClaim =
        document.getElementById("resultClaim");

    if (resultClaim) {
        resultClaim.textContent =
            data.claim || "";
    }


    // --------------------------------------------------------
    // Verdict
    // --------------------------------------------------------

    updateVerdict(
        verdict.verdict || "INSUFFICIENT EVIDENCE"
    );


    // --------------------------------------------------------
    // Counts
    // --------------------------------------------------------

    const supportingCount =
        document.getElementById("supportingCount");

    const contradictingCount =
        document.getElementById("contradictingCount");

    const neutralCount =
        document.getElementById("neutralCount");


    if (supportingCount) {

        supportingCount.textContent =
            verdict.support ??
            verdict.support_count ??
            0;
    }


    if (contradictingCount) {

        contradictingCount.textContent =
            verdict.contradiction ??
            verdict.contradiction_count ??
            0;
    }


    if (neutralCount) {

        neutralCount.textContent =
            verdict.neutral ??
            verdict.neutral_count ??
            0;
    }


    // --------------------------------------------------------
    // Explanation
    // --------------------------------------------------------

    const explanation =
        document.getElementById("explanation");

    if (explanation) {

        explanation.textContent =
            data.explanation ||
            createExplanation(
                verdict,
                sources
            );
    }


    // --------------------------------------------------------
    // Source count
    // --------------------------------------------------------

    const sourceCount =
        document.getElementById("sourceCount");

    if (sourceCount) {

        sourceCount.textContent =
            `${sources.length} sources were checked`;
    }


    // --------------------------------------------------------
    // Sources
    // --------------------------------------------------------

    displaySources(sources);


    // --------------------------------------------------------
    // Show results
    // --------------------------------------------------------

    if (resultSection) {

        resultSection.classList.remove(
            "hidden"
        );

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


// ============================================================
// UPDATE VERDICT
// ============================================================

function updateVerdict(verdict) {

    const verdictCard =
        document.getElementById("verdictCard");

    const verdictIcon =
        document.getElementById("verdictIcon");

    const verdictTitle =
        document.getElementById("verdictTitle");

    const verdictDescription =
        document.getElementById("verdictDescription");


    if (
        !verdictCard ||
        !verdictIcon ||
        !verdictTitle ||
        !verdictDescription
    ) {
        return;
    }


    verdictCard.classList.remove(
        "supported",
        "contradicted",
        "mixed",
        "insufficient"
    );


    // --------------------------------------------------------
    // Supported
    // --------------------------------------------------------

    if (verdict === "LIKELY SUPPORTED") {

        verdictCard.classList.add(
            "supported"
        );

        verdictIcon.textContent = "✓";

        verdictTitle.textContent =
            "Likely Supported";

        verdictDescription.textContent =
            "Most of the available sources support this claim.";
    }


    // --------------------------------------------------------
    // Contradicted
    // --------------------------------------------------------

    else if (
        verdict === "LIKELY CONTRADICTED"
    ) {

        verdictCard.classList.add(
            "contradicted"
        );

        verdictIcon.textContent = "✕";

        verdictTitle.textContent =
            "Likely Contradicted";

        verdictDescription.textContent =
            "Most of the available sources disagree with this claim.";
    }


    // --------------------------------------------------------
    // Mixed
    // --------------------------------------------------------

    else if (
        verdict === "MIXED EVIDENCE"
    ) {

        verdictCard.classList.add(
            "mixed"
        );

        verdictIcon.textContent = "⚠";

        verdictTitle.textContent =
            "Mixed Evidence";

        verdictDescription.textContent =
            "Some sources support this claim while others disagree.";
    }


    // --------------------------------------------------------
    // Insufficient
    // --------------------------------------------------------

    else {

        verdictCard.classList.add(
            "insufficient"
        );

        verdictIcon.textContent = "?";

        verdictTitle.textContent =
            "Not Enough Evidence";

        verdictDescription.textContent =
            "We couldn't find enough clear evidence to make a reliable judgment.";
    }
}


// ============================================================
// CREATE EXPLANATION
// ============================================================

function createExplanation(
    verdict,
    sources
) {

    const support =
        verdict.support ??
        verdict.support_count ??
        0;

    const contradiction =
        verdict.contradiction ??
        verdict.contradiction_count ??
        0;

    const neutral =
        verdict.neutral ??
        verdict.neutral_count ??
        0;

    const total =
        sources.length;


    if (
        verdict.verdict ===
        "LIKELY SUPPORTED"
    ) {

        return (
            `We found ${support} source` +
            `${support === 1 ? "" : "s"} ` +
            `that support this claim. ` +
            `${neutral} source` +
            `${neutral === 1 ? "" : "s"} ` +
            `did not provide enough information to clearly support or reject it.` +
            (total
                ? ` We checked ${total} sources in total.`
                : "")
        );
    }


    if (
        verdict.verdict ===
        "LIKELY CONTRADICTED"
    ) {

        return (
            `We found ${contradiction} source` +
            `${contradiction === 1 ? "" : "s"} ` +
            `that disagree with this claim. ` +
            `${neutral} source` +
            `${neutral === 1 ? "" : "s"} ` +
            `were unclear. ` +
            `We checked ${total} sources in total.`
        );
    }


    if (
        verdict.verdict ===
        "MIXED EVIDENCE"
    ) {

        return (
            `The evidence is divided. ` +
            `${support} source` +
            `${support === 1 ? "" : "s"} ` +
            `support the claim, while ` +
            `${contradiction} source` +
            `${contradiction === 1 ? "" : "s"} ` +
            `disagree with it. ` +
            `This means the claim needs further verification.`
        );
    }


    return (
        `We checked ${total} source` +
        `${total === 1 ? "" : "s"}, ` +
        `but there isn't enough clear evidence ` +
        `to confidently determine whether this claim is true or false.`
    );
}


// ============================================================
// DISPLAY SOURCES
// ============================================================

function displaySources(sources) {

    const sourcesList =
        document.getElementById("sourcesList");

    if (!sourcesList) {
        return;
    }

    sourcesList.innerHTML = "";


    if (!sources.length) {

        sourcesList.innerHTML =
            `<p>No sources were found.</p>`;

        return;
    }


    sources.forEach(
        (source, index) => {

            const sourceCard =
                document.createElement("div");

            sourceCard.className =
                "source-item";


            // ------------------------------------------------
            // Classification
            // ------------------------------------------------

            let classification =
                "Unclear";

            let classificationClass =
                "neutral";


            if (
                source.label === "entailment" ||
                source.category === "supporting"
            ) {

                classification =
                    "Supports claim";

                classificationClass =
                    "supporting";
            }


            else if (
                source.label === "contradiction" ||
                source.category === "contradicting"
            ) {

                classification =
                    "Disagrees with claim";

                classificationClass =
                    "contradicting";
            }


            // ------------------------------------------------
            // Source HTML
            // ------------------------------------------------

            sourceCard.innerHTML = `

                <div class="source-top">

                    <div>

                        <span class="source-number">
                            ${index + 1}
                        </span>

                        <strong>
                            ${escapeHtml(
                                source.source ||
                                "Unknown source"
                            )}
                        </strong>

                    </div>

                    <span class="source-badge ${classificationClass}">
                        ${classification}
                    </span>

                </div>


                <h4>
                    ${escapeHtml(
                        source.headline ||
                        "No headline available"
                    )}
                </h4>


                <p class="source-evidence">
                    ${escapeHtml(
                        source.evidence ||
                        source.explanation ||
                        "No additional evidence available."
                    )}
                </p>


                ${
                    source.link
                    ?
                    `
                    <a
                        href="${escapeAttribute(
                            source.link
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Read source →
                    </a>
                    `
                    :
                    ""
                }

            `;


            sourcesList.appendChild(
                sourceCard
            );
        }
    );
}


// ============================================================
// LOADING
// ============================================================

function showLoading() {

    const loading =
        document.getElementById("loading");

    const resultSection =
        document.getElementById("resultSection");


    if (loading) {

        loading.classList.remove(
            "hidden"
        );
    }


    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );
    }
}


function hideLoading() {

    const loading =
        document.getElementById("loading");

    if (loading) {

        loading.classList.add(
            "hidden"
        );
    }
}


function updateLoadingText(text) {

    const loadingText =
        document.getElementById("loadingText");

    if (loadingText) {

        loadingText.textContent =
            text;
    }
}


// ============================================================
// ERROR
// ============================================================

function showError(message) {

    const errorMessage =
        document.getElementById("errorMessage");

    if (!errorMessage) {
        alert(message);
        return;
    }

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );
}


function hideError() {

    const errorMessage =
        document.getElementById("errorMessage");

    if (!errorMessage) {
        return;
    }

    errorMessage.textContent = "";

    errorMessage.classList.add(
        "hidden"
    );
}


// ============================================================
// RESET
// ============================================================

function resetChecker() {

    const claimInput =
        document.getElementById("claimInput");

    const resultSection =
        document.getElementById("resultSection");


    if (claimInput) {
        claimInput.value = "";
    }


    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );
    }


    hideError();


    if (claimInput) {
        claimInput.focus();
    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


// ============================================================
// SECURITY HELPERS
// ============================================================

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;
}


function escapeAttribute(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}