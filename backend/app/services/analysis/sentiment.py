import re
from typing import List, Dict, Any
from transformers import pipeline
from backend.app.core.config import settings

class SentimentService:
    def __init__(self):
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            # Load the pipeline lazily to save startup time
            self._pipeline = pipeline(
                "sentiment-analysis", 
                model=settings.SENTIMENT_MODEL_NAME
            )
        return self._pipeline

    def _map_label(self, label: str) -> str:
        """
        Maps FinBERT labels (positive, negative, neutral) to contract labels (Bullish, Bearish, Neutral).
        """
        lbl = label.lower()
        if "positive" in lbl or "bullish" in lbl:
            return "Bullish"
        elif "negative" in lbl or "bearish" in lbl:
            return "Bearish"
        else:
            return "Neutral"

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a single block of text and returns label and score.
        """
        if not text or not text.strip():
            return {"label": "Neutral", "score": 0.0}

        try:
            # Keep text within model's context limit
            truncated_text = text[:1500]
            result = self.pipeline(truncated_text)[0]
            return {
                "label": self._map_label(result["label"]),
                "score": float(result["score"])
            }
        except Exception:
            return {"label": "Neutral", "score": 0.0}

    def analyze_section(self, section_text: str) -> Dict[str, Any]:
        """
        Splits section text into chunks (by sentence/paragraph),
        runs FinBERT on each chunk, and aggregates them.
        """
        if not section_text or not section_text.strip():
            return {
                "label": "Neutral",
                "score": 0.0,
                "chunk_scores": []
            }

        # Simple sentence splitter
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', section_text) if s.strip()]
        if not sentences:
            sentences = [section_text]

        chunk_scores = []
        positive_scores = []
        negative_scores = []
        neutral_scores = []
        
        # Accumulate scores for aggregation
        weighted_sum = 0.0
        
        for sentence in sentences:
            res = self.analyze_text(sentence)
            chunk_scores.append({
                "text": sentence,
                "label": res["label"],
                "score": res["score"]
            })
            
            if res["label"] == "Bullish":
                weighted_sum += 1.0 * res["score"]
                positive_scores.append(res["score"])
            elif res["label"] == "Bearish":
                weighted_sum -= 1.0 * res["score"]
                negative_scores.append(res["score"])
            else:
                weighted_sum += 0.0
                neutral_scores.append(res["score"])

        # Determine overall label based on average weight
        avg_weight = weighted_sum / len(sentences)
        
        if avg_weight > 0.15:
            overall_label = "Bullish"
            overall_score = sum(positive_scores) / len(positive_scores) if positive_scores else 0.0
        elif avg_weight < -0.15:
            overall_label = "Bearish"
            overall_score = sum(negative_scores) / len(negative_scores) if negative_scores else 0.0
        else:
            overall_label = "Neutral"
            overall_score = sum(neutral_scores) / len(neutral_scores) if neutral_scores else 0.0

        return {
            "label": overall_label,
            "score": float(overall_score),
            "chunk_scores": chunk_scores
        }


sentiment_service = SentimentService()
