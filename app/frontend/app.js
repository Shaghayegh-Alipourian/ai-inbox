const API_BASE = "/api/v1";

let emails = [];
let selectedEmailId = null;


/* =========================================================
   DOM
========================================================= */

const emailForm = document.querySelector("#email-form");
const subjectInput = document.querySelector("#subject");
const bodyInput = document.querySelector("#body");
const saveEmailButton = document.querySelector("#save-email-btn");
const formStatus = document.querySelector("#form-status");

const emailList = document.querySelector("#email-list");
const inboxCount = document.querySelector("#inbox-count");
const refreshButton = document.querySelector("#refresh-btn");

const selectedEmail = document.querySelector("#selected-email");

const stream = document.querySelector("#stream");
const streamContent = document.querySelector("#stream-content");

const runEvaluationButton = document.querySelector(
    "#run-evaluation-btn",
);
const loadEvaluationButton = document.querySelector(
    "#load-evaluation-btn",
);
const evaluationStatus = document.querySelector(
    "#evaluation-status",
);
const evaluationOutput = document.querySelector(
    "#evaluation-output",
);


/* =========================================================
   Initialization
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    loadEmails();
    loadEvaluationResults();
});


/* =========================================================
   Email Creation
========================================================= */

emailForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const subject = subjectInput.value.trim();
    const body = bodyInput.value.trim();

    if (!subject || !body) {
        setFormStatus("Subject and body are required.", true);
        return;
    }

    setButtonLoading(saveEmailButton, true, "Saving...");

    try {
        const response = await fetch(`${API_BASE}/emails`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                subject,
                body,
            }),
        });

        if (!response.ok) {
            throw new Error(
                `Failed to save email (${response.status}).`,
            );
        }

        const email = await response.json();

        subjectInput.value = "";
        bodyInput.value = "";

        setFormStatus("Email saved successfully.");

        await loadEmails(email.id);
    } catch (error) {
        setFormStatus(error.message, true);
    } finally {
        setButtonLoading(saveEmailButton, false, "Save Email");
    }
});


/* =========================================================
   Email List
========================================================= */

refreshButton.addEventListener("click", () => {
    loadEmails(selectedEmailId);
});


async function loadEmails(selectId = null) {
    try {
        const response = await fetch(`${API_BASE}/emails`);

        if (!response.ok) {
            throw new Error(
                `Failed to load inbox (${response.status}).`,
            );
        }

        emails = await response.json();

        renderEmailList();

        if (selectId !== null) {
            const exists = emails.some(
                (email) => email.id === selectId,
            );

            if (exists) {
                selectEmail(selectId);
                return;
            }
        }

        if (
            selectedEmailId !== null &&
            emails.some((email) => email.id === selectedEmailId)
        ) {
            renderSelectedEmail(
                emails.find(
                    (email) => email.id === selectedEmailId,
                ),
            );
            return;
        }

        if (emails.length > 0) {
            selectEmail(emails[0].id);
        } else {
            selectedEmailId = null;
            renderSelectedEmail(null);
        }
    } catch (error) {
        emailList.innerHTML = `
            <div class="list-empty">
                <div class="empty-icon">!</div>
                <h3>Unable to load inbox</h3>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}


function renderEmailList() {
    inboxCount.textContent = `${emails.length} ${
        emails.length === 1 ? "email" : "emails"
    }`;

    if (emails.length === 0) {
        emailList.innerHTML = `
            <div class="list-empty">
                <div class="empty-icon">✉</div>
                <h3>No emails yet</h3>
                <p>Add your first email above.</p>
            </div>
        `;
        return;
    }

    emailList.innerHTML = emails
        .map((email) => {
            const selected =
                email.id === selectedEmailId
                    ? "email-row selected"
                    : "email-row";

            return `
                <button
                    class="${selected}"
                    data-email-id="${email.id}"
                    type="button"
                >
                    <div class="email-row-top">
                        <span class="email-row-icon">✉</span>

                        <span class="email-date">
                            ${formatDate(email.created_at)}
                        </span>
                    </div>

                    <strong>
                        ${escapeHtml(email.subject)}
                    </strong>

                    <span class="email-preview">
                        ${escapeHtml(
                            truncate(email.body, 100),
                        )}
                    </span>
                </button>
            `;
        })
        .join("");

    document.querySelectorAll(".email-row").forEach((row) => {
        row.addEventListener("click", () => {
            selectEmail(Number(row.dataset.emailId));
        });
    });
}


function selectEmail(emailId) {
    selectedEmailId = emailId;

    const email = emails.find(
        (item) => item.id === emailId,
    );

    if (!email) {
        return;
    }

    renderEmailList();
    renderSelectedEmail(email);
    resetStream();
}


function renderSelectedEmail(email) {
    if (!email) {
        selectedEmail.innerHTML = `
            <div class="selection-empty">
                <div class="empty-icon">⌁</div>
                <h3>Select an email</h3>
                <p>
                    Choose an email from your inbox to inspect it
                    and run AI analysis.
                </p>
            </div>
        `;
        return;
    }

    selectedEmail.innerHTML = `
        <div class="email-detail">
            <div class="email-detail-header">
                <div>
                    <span class="detail-label">SUBJECT</span>
                    <h3>${escapeHtml(email.subject)}</h3>
                </div>

                <span class="email-id">
                    #${email.id}
                </span>
            </div>

            <div class="email-meta">
                <span>
                    Received ${formatDate(email.created_at)}
                </span>
            </div>

            <div class="email-body">
                ${escapeHtml(email.body)}
            </div>

            <button
                id="analyze-selected-btn"
                class="primary-btn analyze-selected-btn"
                type="button"
            >
                ✦ Analyze Email
            </button>
        </div>
    `;

    document
        .querySelector("#analyze-selected-btn")
        .addEventListener("click", () => {
            analyzeSelectedEmail(email.id);
        });
}


/* =========================================================
   AI Analysis
========================================================= */

async function analyzeSelectedEmail(emailId) {
    const button = document.querySelector(
        "#analyze-selected-btn",
    );

    if (button) {
        setButtonLoading(button, true, "Analyzing...");
    }

    stream.innerHTML = `
        <div id="stream-content" class="stream-content">
            <div class="loading-spinner"></div>

            <h3 class="stream-title">
                Analyzing email...
            </h3>

            <p class="stream-description">
                The AI is classifying the message, extracting
                information, and generating a suggested reply.
            </p>
        </div>
    `;

    try {
        const response = await fetch(
            `${API_BASE}/emails/${emailId}/analyze/stream`,
        );

        if (!response.ok) {
            throw new Error(
                `Analysis request failed (${response.status}).`,
            );
        }

        if (!response.body) {
            throw new Error("Streaming is not supported.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";
        let rawContent = "";

        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(value, {
                stream: true,
            });

            const events = buffer.split("\n\n");
            buffer = events.pop() || "";

            for (const event of events) {
                const content = handleStreamEvent(
                    event,
                    rawContent,
                );

                if (content !== null) {
                    rawContent = content;
                }
            }
        }

        if (buffer.trim()) {
            const content = handleStreamEvent(
                buffer,
                rawContent,
            );

            if (content !== null) {
                rawContent = content;
            }
        }

        renderAnalysisResult(rawContent);
    } catch (error) {
        renderStreamError(error.message);
    } finally {
        if (button) {
            setButtonLoading(
                button,
                false,
                "✦ Analyze Email",
            );
        }
    }
}


function handleStreamEvent(event, currentContent) {
    const line = event
        .split("\n")
        .find((item) => item.startsWith("data: "));

    if (!line) {
        return null;
    }

    try {
        const payload = JSON.parse(
            line.slice("data: ".length),
        );

        if (payload.type === "chunk") {
            return currentContent + payload.content;
        }

        return currentContent;
    } catch {
        return currentContent;
    }
}


function renderAnalysisResult(rawContent) {
    let analysis;

    try {
        analysis = JSON.parse(rawContent);
    } catch {
        renderStreamError(
            "The AI returned an invalid structured response.",
        );
        return;
    }

    stream.innerHTML = `
        <div class="stream-result">
            <div class="analysis-result">

                <div class="analysis-result-header">
                    <div>
                        <span class="analysis-eyebrow">
                            ANALYSIS COMPLETED
                        </span>

                        <h3>AI Analysis</h3>
                    </div>

                    <span class="confidence-badge">
                        ${formatPercent(analysis.confidence)}
                        confidence
                    </span>
                </div>


                <div class="analysis-grid">

                    ${createAnalysisItem(
                        "Category",
                        formatLabel(analysis.category),
                        "category",
                    )}

                    ${createAnalysisItem(
                        "Priority",
                        formatLabel(analysis.priority),
                        `priority-${escapeHtml(
                            analysis.priority,
                        )}`,
                    )}

                    ${createAnalysisItem(
                        "Action Required",
                        analysis.action_required
                            ? "Yes"
                            : "No",
                        analysis.action_required
                            ? "action-yes"
                            : "action-no",
                    )}

                    ${createAnalysisItem(
                        "Invoice ID",
                        analysis.invoice_id ||
                            "Not found",
                        "default",
                    )}

                    ${createAnalysisItem(
                        "Due Date",
                        analysis.due_date ||
                            "Not specified",
                        "default",
                    )}

                </div>


                <div class="reply-section">
                    <span class="analysis-eyebrow">
                        SUGGESTED REPLY
                    </span>

                    <div class="reply-box">
                        ${escapeHtml(
                            analysis.suggested_reply,
                        )}
                    </div>
                </div>

            </div>
        </div>
    `;
}


function createAnalysisItem(label, value, className) {
    return `
        <div class="analysis-item">
            <span class="analysis-item-label">
                ${escapeHtml(label)}
            </span>

            <span class="analysis-item-value ${className}">
                ${escapeHtml(value)}
            </span>
        </div>
    `;
}


function resetStream() {
    stream.innerHTML = `
        <div id="stream-content" class="stream-content">
            <div class="stream-symbol">✦</div>

            <h3 class="stream-title">
                Ready to analyze
            </h3>

            <p class="stream-description">
                Click <strong>Analyze Email</strong> on the
                selected message.
            </p>
        </div>
    `;
}


function renderStreamError(message) {
    stream.innerHTML = `
        <div class="stream-content">
            <div class="error-symbol">!</div>

            <h3 class="stream-title">
                Analysis failed
            </h3>

            <p class="stream-description">
                ${escapeHtml(message)}
            </p>
        </div>
    `;
}


/* =========================================================
   Evaluation
========================================================= */

runEvaluationButton.addEventListener(
    "click",
    runEvaluation,
);

loadEvaluationButton.addEventListener(
    "click",
    loadEvaluationResults,
);


async function runEvaluation() {
    setButtonLoading(
        runEvaluationButton,
        true,
        "Running...",
    );

    evaluationStatus.textContent =
        "Running Prompt V1 evaluation...";

    try {
        await runEvaluationPrompt("v1");

        evaluationStatus.textContent =
            "Running Prompt V2 evaluation...";

        await runEvaluationPrompt("v2");

        evaluationStatus.textContent =
            "Evaluation completed.";

        await loadEvaluationResults();
    } catch (error) {
        evaluationStatus.textContent =
            error.message;
    } finally {
        setButtonLoading(
            runEvaluationButton,
            false,
            "▶ Run Evaluation",
        );
    }
}


async function runEvaluationPrompt(promptVersion) {
    const response = await fetch(
        `${API_BASE}/evaluation/run`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                dataset_path:
                    "data/golden/emails.jsonl",
                prompt_version: promptVersion,
            }),
        },
    );

    if (!response.ok) {
        const payload = await response
            .json()
            .catch(() => ({}));

        throw new Error(
            payload.detail ||
                `Evaluation failed (${response.status}).`,
        );
    }

    return response.json();
}


async function loadEvaluationResults() {
    try {
        const response = await fetch(
            `${API_BASE}/evaluation/compare`,
        );

        if (!response.ok) {
            throw new Error(
                `Failed to load evaluation results (${response.status}).`,
            );
        }

        const comparison = await response.json();

        renderEvaluation(comparison);
    } catch (error) {
        evaluationOutput.innerHTML = `
            <div class="evaluation-empty error-state">
                <div class="empty-icon">!</div>

                <h3>Unable to load evaluation</h3>

                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}


function renderEvaluation(comparison) {
    const v1 = comparison.prompt_v1;
    const v2 = comparison.prompt_v2;

    if (!v1 && !v2) {
        evaluationOutput.innerHTML = `
            <div class="evaluation-empty">
                <div class="empty-icon">▥</div>

                <h3>No evaluation runs found</h3>

                <p>
                    Run an evaluation to compare Prompt V1 and V2.
                </p>
            </div>
        `;
        return;
    }

    const best = chooseBestPrompt(v1, v2);

    evaluationOutput.innerHTML = `
        <div class="evaluation-summary">

            <div>
                <span class="analysis-eyebrow">
                    BEST PROMPT
                </span>

                <strong>
                    ${best ? best.prompt_version.toUpperCase() : "—"}
                </strong>
            </div>

            <div>
                <span class="analysis-eyebrow">
                    EVALUATED CASES
                </span>

                <strong>
                    ${best ? best.total_cases : "—"}
                </strong>
            </div>

            <div>
                <span class="analysis-eyebrow">
                    MODEL
                </span>

                <strong>
                    ${best ? escapeHtml(best.model) : "—"}
                </strong>
            </div>

        </div>

        <div class="evaluation-grid">
            ${v1 ? createEvaluationCard(v1) : ""}
            ${v2 ? createEvaluationCard(v2) : ""}
        </div>
    `;
}


function createEvaluationCard(run) {
    const metrics = run.metrics;

    return `
        <article class="evaluation-result">

            <div class="evaluation-result-header">
                <div>
                    <h3>
                        Prompt ${escapeHtml(
                            run.prompt_version.toUpperCase(),
                        )}
                    </h3>

                    <span class="model-name">
                        ${escapeHtml(run.provider)}
                        ·
                        ${escapeHtml(run.model)}
                    </span>
                </div>

                <span class="status-badge">
                    ${run.successful_cases}/${run.total_cases}
                    passed
                </span>
            </div>

            <div class="metrics">

                ${metric(
                    "Classification",
                    formatPercent(
                        metrics.classification_accuracy,
                    ),
                )}

                ${metric(
                    "Priority",
                    formatPercent(
                        metrics.priority_accuracy,
                    ),
                )}

                ${metric(
                    "Extraction",
                    formatPercent(
                        metrics.extraction_accuracy,
                    ),
                )}

                ${metric(
                    "Action Required",
                    formatPercent(
                        metrics.action_required_accuracy,
                    ),
                )}

                ${metric(
                    "Structured Output",
                    formatPercent(
                        metrics.structured_output_validity,
                    ),
                )}

                ${metric(
                    "Response Quality",
                    formatPercent(
                        metrics.response_quality,
                    ),
                )}

                ${metric(
                    "Latency",
                    `${Math.round(
                        metrics.average_latency_ms,
                    )} ms`,
                )}

                ${metric(
                    "TTFT",
                    `${Math.round(
                        metrics.average_ttft_ms,
                    )} ms`,
                )}

                ${metric(
                    "Input Tokens",
                    Math.round(
                        metrics.average_input_tokens,
                    ),
                )}

                ${metric(
                    "Output Tokens",
                    Math.round(
                        metrics.average_output_tokens,
                    ),
                )}

                ${metric(
                    "Average Cost",
                    `$${Number(
                        metrics.average_cost,
                    ).toFixed(6)}`,
                )}

            </div>
        </article>
    `;
}


function metric(label, value) {
    return `
        <div class="metric">
            <span class="metric-label">
                ${escapeHtml(label)}
            </span>

            <strong class="metric-value">
                ${escapeHtml(String(value))}
            </strong>
        </div>
    `;
}


function chooseBestPrompt(v1, v2) {
    if (!v1) return v2;
    if (!v2) return v1;

    const score1 = calculateOverallScore(v1);
    const score2 = calculateOverallScore(v2);

    return score2 > score1 ? v2 : v1;
}


function calculateOverallScore(run) {
    const metrics = run.metrics;

    return (
        metrics.classification_accuracy +
        metrics.priority_accuracy +
        metrics.extraction_accuracy +
        metrics.action_required_accuracy +
        metrics.structured_output_validity +
        metrics.response_quality
    ) / 6;
}


/* =========================================================
   Helpers
========================================================= */

function setFormStatus(message, isError = false) {
    formStatus.textContent = message;
    formStatus.className = isError
        ? "form-status error-text"
        : "form-status success-text";
}


function setButtonLoading(button, loading, text) {
    button.disabled = loading;
    button.textContent = text;
}


function formatDate(value) {
    if (!value) {
        return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Unknown date";
    }

    return date.toLocaleDateString(
        undefined,
        {
            year: "numeric",
            month: "short",
            day: "numeric",
        },
    );
}


function formatPercent(value) {
    const numeric = Number(value);

    if (!Number.isFinite(numeric)) {
        return "—";
    }

    return `${(numeric * 100).toFixed(2)}%`;
}


function formatLabel(value) {
    if (!value) {
        return "Unknown";
    }

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) =>
            letter.toUpperCase(),
        );
}


function truncate(value, length) {
    if (!value || value.length <= length) {
        return value || "";
    }

    return `${value.slice(0, length)}...`;
}


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

