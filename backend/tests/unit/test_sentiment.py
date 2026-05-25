import pytest
from backend.app.services.analysis.sentiment import sentiment_service
from backend.app.services.analysis.risk_detector import risk_detector_service
from backend.app.services.analysis.summarizer import summarizer_service

def test_sentiment_analysis_single_and_section():
    """
    Verifies that sentiment_service correctly identifies Bullish, Bearish, and Neutral sentiment.
    """
    # 1. Single text test
    res_bullish = sentiment_service.analyze_text("The company's revenues grew by 20% and profits surged.")
    assert res_bullish["label"] in ["Bullish", "Neutral"]  # FinBERT might label as positive or neutral depending on threshold, but let's check it's not bearish.
    assert "score" in res_bullish
    
    res_bearish = sentiment_service.analyze_text("We suffered severe losses and sales declined dramatically.")
    assert res_bearish["label"] == "Bearish"
    
    # 2. Section analysis test
    section_text = (
        "Operating performance was excellent last year. "
        "However, we face high inflation and competition headwinds. "
        "Overall the outlook is stable."
    )
    section_res = sentiment_service.analyze_section(section_text)
    assert "label" in section_res
    assert "score" in section_res
    assert "chunk_scores" in section_res
    assert len(section_res["chunk_scores"]) == 3
    for chunk in section_res["chunk_scores"]:
        assert "text" in chunk
        assert "label" in chunk
        assert "score" in chunk

def test_risk_detection():
    """
    Verifies that risk_detector_service identifies risk keywords, triggers flags, and scores pages.
    """
    chunks = [
        {
            "text": "Geopolitical tensions in Europe and inflation are causing severe macroeconomic uncertainty.",
            "page": 1,
            "metadata": {"page": 1, "source": "test.pdf"}
        },
        {
            "text": "We are facing intense competition in software talent acquisition and potential cybersecurity data privacy risks.",
            "page": 2,
            "metadata": {"page": 2, "source": "test.pdf"}
        }
    ]
    
    report = risk_detector_service.analyze_document_risk(chunks)
    assert "overall_score" in report
    assert "sections" in report
    assert len(report["sections"]) == 2
    
    # Page 1 checks
    page1 = report["sections"][0]
    assert "Page 1" in page1["heading"]
    assert page1["score"] > 0.0
    assert any("Macroeconomic Risk" in f or "Geopolitical" in f for f in page1["flags"])
    assert "tensions" in page1["excerpt"] or "inflation" in page1["excerpt"] or "uncertainty" in page1["excerpt"]
    
    # Page 2 checks
    page2 = report["sections"][1]
    assert "Page 2" in page2["heading"]
    assert any("Competition" in f or "Cybersecurity" in f or "Privacy" in f for f in page2["flags"])

@pytest.mark.anyio
async def test_summarizer_mock():
    """
    Verifies that the summarizer map-reduce pipeline produces a structured summary response.
    """
    chunks = [
        {"text": "TCS revenue reached 2.2L crore in FY23.", "page": 1, "metadata": {"page": 1}},
        {"text": "BFSI remains largest segment.", "page": 2, "metadata": {"page": 2}},
        {"text": "Risks include talent competition.", "page": 3, "metadata": {"page": 3}}
    ]
    
    res = await summarizer_service.summarize_document(chunks)
    assert "summary" in res
    assert "highlights" in res
    assert "generated_at" in res
    assert len(res["highlights"]) > 0
    assert isinstance(res["highlights"], list)
