import re
from typing import List, Dict, Any
import spacy
from backend.app.core.config import settings

class RiskDetectorService:
    def __init__(self):
        self._nlp = None
        # Core financial risk keywords mapped to category/flag labels
        self.risk_keywords = {
            "geopolitical": "Geopolitical Tension",
            "inflation": "Macroeconomic Risk",
            "uncertainty": "Macroeconomic Risk",
            "competition": "Market Competition",
            "competitor": "Market Competition",
            "cybersecurity": "Cybersecurity Threat",
            "data privacy": "Data Privacy Concern",
            "litigation": "Legal Risk",
            "lawsuit": "Legal Risk",
            "regulation": "Regulatory Compliance Risk",
            "compliance": "Regulatory Compliance Risk",
            "volatility": "Financial Volatility",
            "decline": "Financial Volatility",
            "loss": "Financial Loss Alert",
            "threat": "Security Threat"
        }

    @property
    def nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load(settings.SPACY_MODEL_NAME)
            except OSError:
                from spacy.cli import download
                download(settings.SPACY_MODEL_NAME)
                self._nlp = spacy.load(settings.SPACY_MODEL_NAME)
        return self._nlp

    def analyze_document_risk(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Groups chunks by page (treating each page as a section),
        scans for risks via keywords and spaCy NER, and returns a detailed report.
        """
        if not chunks:
            return {"overall_score": 0.0, "sections": []}

        # Group chunks by page number
        page_chunks: Dict[int, List[Dict[str, Any]]] = {}
        for chunk in chunks:
            # support both formats (direct JSON keys or nested metadata keys)
            page = chunk.get("page") or chunk.get("metadata", {}).get("page", 1)
            page_chunks.setdefault(page, []).append(chunk)

        sections_report = []
        overall_scores = []

        for page, chks in sorted(page_chunks.items()):
            # Combine text of this page
            page_text = " ".join([c["text"] for c in chks])
            
            # 1. Determine Section Heading
            # Look for common section headers in the text, or extract the first sentence
            heading = f"Page {page}"
            first_line = page_text.split("\n")[0].strip()
            if len(first_line) > 5 and len(first_line) < 60:
                heading = f"Page {page}: {first_line}"
            else:
                # check if there are known headers like Risk Factors or Financial Highlights
                for keyword in ["financial highlights", "business segment", "risk factors", "outlook"]:
                    if keyword in page_text.lower():
                        heading = f"Page {page}: {keyword.title()}"
                        break

            # 2. Keyword matching & Flag generation
            flags = set()
            found_excerpts = []
            keyword_count = 0
            
            # Simple word-based regex search for keywords
            for kw, flag_label in self.risk_keywords.items():
                pattern = re.compile(rf"\b{kw}s?\b", re.IGNORECASE)
                matches = list(pattern.finditer(page_text))
                if matches:
                    flags.add(flag_label)
                    keyword_count += len(matches)
                    # Extract a small excerpt around the first match
                    first_match = matches[0]
                    start = max(0, first_match.start() - 60)
                    end = min(len(page_text), first_match.end() + 60)
                    excerpt = page_text[start:end].strip().replace("\n", " ")
                    found_excerpts.append(f"... {excerpt} ...")

            # 3. Named Entity Recognition (NER) analysis
            # Look for MONEY, LAW, ORG, and GPE entities to adjust risk scores
            doc = self.nlp(page_text[:4000])  # limit to 4000 chars for NER speed
            ner_risk_multiplier = 1.0
            
            for ent in doc.ents:
                if ent.label_ == "LAW":
                    flags.add("Legal/Regulatory Entity")
                    ner_risk_multiplier += 0.05
                elif ent.label_ == "MONEY" and any(w in ent.text.lower() for w in ["crore", "billion", "million"]):
                    # If high money mentions exist in a risky section, elevate priority
                    ner_risk_multiplier += 0.02
                elif ent.label_ == "GPE" and any(w in page_text.lower() for w in ["tension", "conflict", "uncertainty"]):
                    flags.add("Geopolitical Exposure")
                    ner_risk_multiplier += 0.05

            # 4. Calculate Risk Score (0.0 to 1.0)
            # Base score depends on keyword count
            base_score = min(1.0, (keyword_count / 8.0))
            score = min(1.0, base_score * ner_risk_multiplier)
            score = round(score, 2)
            
            # Excerpt formatting
            combined_excerpt = " | ".join(found_excerpts[:2]) if found_excerpts else "No immediate risk flags detected."

            sections_report.append({
                "heading": heading,
                "score": score,
                "flags": sorted(list(flags)),
                "excerpt": combined_excerpt
            })
            overall_scores.append(score)

        overall_score = round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0.0

        return {
            "overall_score": overall_score,
            "sections": sections_report
        }


risk_detector_service = RiskDetectorService()
