"""
============================================================
  AI-Based Sentiment Analyzer — Flask Application Entry Point
  Internship Project | Uses HuggingFace Transformers + MongoDB
============================================================
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json

# --- Local Modules ---
from models.sentiment_model import SentimentModel
from utils.db import MongoDBClient
from utils.chart_generator import generate_pie_chart, generate_bar_chart
from utils.helpers import sanitize_text, format_confidence

# ── App Initialization ──────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "sentiment_analyzer_internship_2024"

# ── Initialize Sentiment Model (loaded once at startup) ────────────────────
print("[*] Loading HuggingFace sentiment model...")
model = SentimentModel()
print("[✓] Model loaded successfully.")

# ── Initialize MongoDB Connection ───────────────────────────────────────────
db_client = MongoDBClient()
print("[✓] MongoDB connection established.")


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home page — Sentiment analysis input form."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /analyze
    Accepts JSON: { "text": "..." }
    Returns: sentiment label, confidence score, chart data
    """
    data = request.get_json()
    if not data or "text" not in data or not data["text"].strip():
        return jsonify({"error": "Please provide valid text to analyze."}), 400

    raw_text = sanitize_text(data["text"])

    # Run Inference
    result = model.predict(raw_text)
    label      = result["label"]        # POSITIVE / NEGATIVE / NEUTRAL
    confidence = result["confidence"]   # float 0.0 – 1.0
    all_scores = result["all_scores"]   # { POSITIVE: x, NEGATIVE: y, NEUTRAL: z }

    # Persist to MongoDB
    record = {
        "text":       raw_text,
        "label":      label,
        "confidence": confidence,
        "all_scores": all_scores,
        "timestamp":  datetime.utcnow().isoformat(),
        "source":     data.get("source", "manual"),   # e.g. "twitter", "amazon", "manual"
    }
    doc_id = db_client.insert_analysis(record)

    return jsonify({
        "id":         str(doc_id),
        "text":       raw_text,
        "label":      label,
        "confidence": format_confidence(confidence),
        "all_scores": {k: round(v * 100, 2) for k, v in all_scores.items()},
    })


@app.route("/history")
def history():
    """Analysis history page — shows past analyses with charts."""
    records  = db_client.get_all_analyses(limit=50)
    summary  = db_client.get_summary_stats()

    # Generate charts as base64 image strings
    pie_chart = generate_pie_chart(summary["label_counts"])
    bar_chart = generate_bar_chart(summary["daily_counts"])

    return render_template(
        "history.html",
        records   = records,
        summary   = summary,
        pie_chart = pie_chart,
        bar_chart = bar_chart,
    )


@app.route("/api/history", methods=["GET"])
def api_history():
    """JSON endpoint — returns recent analysis records."""
    limit   = int(request.args.get("limit", 20))
    records = db_client.get_all_analyses(limit=limit)
    return jsonify(records)


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """JSON endpoint — returns aggregate statistics."""
    summary = db_client.get_summary_stats()
    return jsonify(summary)


@app.route("/delete/<doc_id>", methods=["DELETE"])
def delete_record(doc_id):
    """DELETE /delete/<id> — removes a single analysis record."""
    deleted = db_client.delete_analysis(doc_id)
    if deleted:
        return jsonify({"message": "Record deleted."})
    return jsonify({"error": "Record not found."}), 404


# ── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
