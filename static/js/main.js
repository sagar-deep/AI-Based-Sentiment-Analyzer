/**
 * SentimentAI — Analyzer Page JS
 * Handles: text input, tab switching, sample chips, API calls, result display
 */

// ── DOM References ──────────────────────────────────────────────────────────
const textInput       = document.getElementById("textInput");
const charCount       = document.getElementById("charCount");
const analyzeBtn      = document.getElementById("analyzeBtn");
const clearBtn        = document.getElementById("clearBtn");
const analyzeAnotherBtn = document.getElementById("analyzeAnotherBtn");
const resultCard      = document.getElementById("resultCard");
const loadingOverlay  = document.getElementById("loadingOverlay");
const sourceTabs      = document.getElementById("sourceTabs");

// Result elements
const resultEmoji       = document.getElementById("resultEmoji");
const resultLabel       = document.getElementById("resultLabel");
const resultSource      = document.getElementById("resultSource");
const confidenceText    = document.getElementById("confidenceText");
const confidenceBar     = document.getElementById("confidenceBar");
const posBar = document.getElementById("posBar");
const negBar = document.getElementById("negBar");
const neuBar = document.getElementById("neuBar");
const posScore = document.getElementById("posScore");
const negScore = document.getElementById("negScore");
const neuScore = document.getElementById("neuScore");
const resultTextPreview = document.getElementById("resultTextPreview");

// ── State ───────────────────────────────────────────────────────────────────
let currentSource = "manual";

// ── Emoji & Color Maps ──────────────────────────────────────────────────────
const EMOJIS = { POSITIVE: "😊", NEGATIVE: "😞", NEUTRAL: "😐" };
const LABEL_COLORS = { POSITIVE: "positive", NEGATIVE: "negative", NEUTRAL: "neutral" };

// ── Character Counter ───────────────────────────────────────────────────────
textInput.addEventListener("input", () => {
  charCount.textContent = textInput.value.length;
});

// ── Source Tab Switching ────────────────────────────────────────────────────
sourceTabs.addEventListener("click", (e) => {
  const tab = e.target.closest(".tab");
  if (!tab) return;
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  tab.classList.add("active");
  currentSource = tab.dataset.source;

  // Update placeholder hint
  const hints = {
    manual:  "Type or paste any text to analyze…",
    twitter: "Paste a tweet or social media post…",
    amazon:  "Paste a product review from Amazon, Flipkart, etc…",
  };
  textInput.placeholder = hints[currentSource] || hints.manual;
});

// ── Sample Chips ────────────────────────────────────────────────────────────
document.querySelectorAll(".sample-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    textInput.value = chip.dataset.text;
    charCount.textContent = textInput.value.length;
    textInput.focus();
  });
});

// ── Clear Button ────────────────────────────────────────────────────────────
clearBtn.addEventListener("click", () => {
  textInput.value = "";
  charCount.textContent = "0";
  textInput.focus();
});

// ── Analyze Button ───────────────────────────────────────────────────────────
analyzeBtn.addEventListener("click", runAnalysis);
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) runAnalysis();
});

// ── Analyze Another ─────────────────────────────────────────────────────────
analyzeAnotherBtn.addEventListener("click", () => {
  resultCard.classList.add("hidden");
  textInput.value = "";
  charCount.textContent = "0";
  textInput.focus();
});

// ── Main Analysis Function ───────────────────────────────────────────────────
async function runAnalysis() {
  const text = textInput.value.trim();
  if (!text) {
    shakeInput();
    return;
  }

  // Show loading
  loadingOverlay.classList.remove("hidden");
  analyzeBtn.disabled = true;

  try {
    const response = await fetch("/analyze", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ text, source: currentSource }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Server error");
    }

    const data = await response.json();
    displayResult(data);

  } catch (error) {
    alert(`Analysis failed: ${error.message}`);
    console.error("[SentimentAI] Error:", error);
  } finally {
    loadingOverlay.classList.add("hidden");
    analyzeBtn.disabled = false;
  }
}

// ── Display Result ───────────────────────────────────────────────────────────
function displayResult(data) {
  const { label, confidence, all_scores, source, text } = data;

  // Emoji & label
  resultEmoji.textContent = EMOJIS[label] || "🤔";
  resultLabel.textContent = label;
  resultLabel.className   = `result-label ${LABEL_COLORS[label] || ""}`;
  resultSource.textContent = `${(source || "manual").replace("_", " ")} input`;

  // Confidence bar — strip "%" and animate
  const confPct = parseFloat(confidence);
  confidenceText.textContent = confidence;
  requestAnimationFrame(() => {
    confidenceBar.style.width = confPct + "%";
  });

  // Breakdown bars
  const pos = all_scores["POSITIVE"] || 0;
  const neg = all_scores["NEGATIVE"] || 0;
  const neu = all_scores["NEUTRAL"]  || 0;

  requestAnimationFrame(() => {
    posBar.style.width = pos + "%";
    negBar.style.width = neg + "%";
    neuBar.style.width = neu + "%";
  });

  posScore.textContent = pos.toFixed(1) + "%";
  negScore.textContent = neg.toFixed(1) + "%";
  neuScore.textContent = neu.toFixed(1) + "%";

  // Text preview (truncated)
  resultTextPreview.textContent = text.length > 120
    ? text.slice(0, 120) + "…"
    : text;

  // Show result card
  resultCard.classList.remove("hidden");
  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── Shake animation for empty input ─────────────────────────────────────────
function shakeInput() {
  const wrap = document.querySelector(".input-group");
  wrap.style.animation = "none";
  requestAnimationFrame(() => {
    wrap.style.animation = "shake 0.3s ease";
  });
}

// Inject shake keyframes
const style = document.createElement("style");
style.textContent = `
@keyframes shake {
  0%,100% { transform: translateX(0); }
  20%      { transform: translateX(-6px); }
  60%      { transform: translateX(6px); }
}`;
document.head.appendChild(style);
