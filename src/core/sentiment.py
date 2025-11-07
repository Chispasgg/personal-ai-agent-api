"""
Sentiment analysis for detecting user emotions.
Simple lexicon-based approach with extensibility for ML models.
"""
from typing import Literal
from textblob import TextBlob
from config.settings import settings

Sentiment = Literal["negative", "neutral", "positive"]


class SentimentAnalyzer:
    """
    Sentiment analyzer using TextBlob.
    Can be extended with more sophisticated models.
    """

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.negative_threshold = settings.sentiment_threshold_negative
        self.positive_threshold = settings.sentiment_threshold_positive

    def analyze(self, text: str) -> tuple[Sentiment, float]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (sentiment_label, polarity_score)
            polarity_score ranges from -1 (negative) to 1 (positive)
        """
        if not text or len(text.strip()) < 2:
            return "neutral", 0.0

        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            # Classify based on thresholds
            if polarity < self.negative_threshold:
                sentiment = "negative"
            elif polarity > self.positive_threshold:
                sentiment = "positive"
            else:
                sentiment = "neutral"

            print(f"Sentiment analysis: text='{text[:50]}...', polarity={polarity:.3f}, sentiment={sentiment}")

            return sentiment, polarity  # type: ignore

        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return "neutral", 0.0

    def is_frustrated(self, text: str, threshold: float=-0.5) -> bool:
        """
        Check if user appears frustrated based on sentiment.

        Args:
            text: Input text
            threshold: Polarity threshold for frustration (default: -0.5)

        Returns:
            True if user appears frustrated
        """
        sentiment, polarity = self.analyze(text)
        return sentiment == "negative" and polarity < threshold

    def get_empathy_level(self, text: str) -> Literal["low", "medium", "high"]:
        """
        Determine appropriate empathy level based on sentiment.

        Args:
            text: Input text

        Returns:
            Empathy level to use in response
        """
        sentiment, polarity = self.analyze(text)

        if sentiment == "negative":
            if polarity < -0.5:
                return "high"
            return "medium"
        elif sentiment == "positive":
            return "low"
        return "medium"


# Global sentiment analyzer instance
_analyzer: SentimentAnalyzer | None = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """
    Get global sentiment analyzer instance.

    Returns:
        SentimentAnalyzer instance
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def analyze_sentiment(text: str) -> tuple[Sentiment, float]:
    """
    Convenience function for sentiment analysis.

    Args:
        text: Input text

    Returns:
        Tuple of (sentiment_label, polarity_score)
    """
    analyzer = get_sentiment_analyzer()
    return analyzer.analyze(text)
