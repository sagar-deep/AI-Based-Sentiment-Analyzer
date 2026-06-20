"""
============================================================
  models/sentiment_model.py
  Wraps HuggingFace pipeline for 3-class sentiment analysis.
  Model: cardiffnlp/twitter-roberta-base-sentiment-latest
         (POSITIVE / NEGATIVE / NEUTRAL)
============================================================
"""

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch


# Label mapping from model output IDs → human-readable labels
LABEL_MAP = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE",
    # Some models already return readable labels:
    "negative": "NEGATIVE",
    "neutral":  "NEUTRAL",
    "positive": "POSITIVE",
}

# Emoji map for UI display
LABEL_EMOJI = {
    "POSITIVE": "😊",
    "NEGATIVE": "😞",
    "NEUTRAL":  "😐",
}


class SentimentModel:
    """
    Singleton wrapper around a HuggingFace zero-shot or classification pipeline.

    Usage:
        model = SentimentModel()
        result = model.predict("This product is amazing!")
        # {'label': 'POSITIVE', 'confidence': 0.97, 'all_scores': {...}}
    """

    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __init__(self):
        """Load model and tokenizer; fall back to distilbert if unavailable."""
        try:
            self.pipe = pipeline(
                task             = "sentiment-analysis",
                model            = self.MODEL_NAME,
                tokenizer        = self.MODEL_NAME,
                top_k            = None,          # return all class scores
                truncation       = True,
                max_length       = 512,
                device           = 0 if torch.cuda.is_available() else -1,
            )
            print(f"  → Using model: {self.MODEL_NAME}")
        except Exception as e:
            # Fallback: lightweight distilbert (binary pos/neg)
            print(f"  [!] Primary model failed ({e}). Falling back to distilbert.")
            self.pipe = pipeline(
                task       = "sentiment-analysis",
                model      = "distilbert-base-uncased-finetuned-sst-2-english",
                top_k      = None,
                truncation = True,
                max_length = 512,
            )

    def predict(self, text: str) -> dict:
        """
        Run inference on a single text string.

        Args:
            text (str): Input text (tweet, review, comment, etc.)

        Returns:
            dict: {
                "label":      "POSITIVE" | "NEGATIVE" | "NEUTRAL",
                "confidence": float,          # winning class score (0–1)
                "all_scores": {               # all class probabilities
                    "POSITIVE": float,
                    "NEGATIVE": float,
                    "NEUTRAL":  float,
                }
            }
        """
        raw_output = self.pipe(text)

        # pipeline with top_k=None returns [[{label, score}, ...]]
        if isinstance(raw_output, list) and isinstance(raw_output[0], list):
            scores_list = raw_output[0]
        else:
            scores_list = raw_output

        # Normalize labels
        all_scores = {}
        for item in scores_list:
            human_label = LABEL_MAP.get(item["label"].upper(),
                          LABEL_MAP.get(item["label"].lower(), item["label"].upper()))
            all_scores[human_label] = item["score"]

        # If NEUTRAL missing (binary model), approximate it
        if "NEUTRAL" not in all_scores:
            pos = all_scores.get("POSITIVE", 0.0)
            neg = all_scores.get("NEGATIVE", 0.0)
            # Neutral score = confidence near 0.5 for both
            neutral_approx = max(0.0, 1.0 - abs(pos - neg) - max(pos, neg) * 0.3)
            # Renormalise
            total = pos + neg + neutral_approx
            all_scores = {
                "POSITIVE": round(pos / total, 4),
                "NEGATIVE": round(neg / total, 4),
                "NEUTRAL":  round(neutral_approx / total, 4),
            }

        # Winning label
        winning_label = max(all_scores, key=all_scores.get)
        confidence    = all_scores[winning_label]

        return {
            "label":      winning_label,
            "confidence": round(confidence, 4),
            "all_scores": all_scores,
            "emoji":      LABEL_EMOJI.get(winning_label, ""),
        }
