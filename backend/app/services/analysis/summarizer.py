import datetime
import os
import asyncio
from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.services.generation.chain import get_anthropic_client


class SummarizerService:
    async def _summarize_text_block(self, text: str, max_words: int = 150) -> str:
        """
        Maps a single section/page text block to a brief summary using Claude.
        """
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "dummy-key":
            return f"Simulated section summary for text block of length {len(text)}."

        client = get_anthropic_client()
        system_prompt = (
            "You are a financial analyst. Summarize the following section of an annual report "
            f"in less than {max_words} words. Focus on financial statistics, metrics, and strategy."
        )
        try:
            response = await client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=300,
                temperature=0.0,
                system=system_prompt,
                messages=[{"role": "user", "content": text}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"[Error summarizing section: {str(e)}]"

    async def summarize_document(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs a map-reduce pipeline:
        1. Map: Summarize each page/section's chunks.
        2. Reduce: Summarize the combined section summaries into a final summary and bulleted highlights.
        """
        generated_at = datetime.datetime.utcnow().isoformat() + "Z"

        if not chunks:
            return {
                "summary": "No document chunks available to summarize.",
                "highlights": [],
                "generated_at": generated_at
            }

        # Group chunks by page number
        page_chunks: Dict[int, List[Dict[str, Any]]] = {}
        for chunk in chunks:
            page = chunk.get("page") or chunk.get("metadata", {}).get("page", 1)
            page_chunks.setdefault(page, []).append(chunk)

        # Sort pages
        sorted_pages = sorted(page_chunks.keys())
        
        # 1. Map Step (in parallel)
        map_tasks = []
        for page in sorted_pages:
            combined_text = " ".join([c["text"] for c in page_chunks[page]])
            map_tasks.append(self._summarize_text_block(combined_text))

        section_summaries = await asyncio.gather(*map_tasks)
        combined_summaries_text = "\n\n".join(
            [f"--- Page {page} Summary ---\n{summary}" for page, summary in zip(sorted_pages, section_summaries)]
        )

        # 2. Reduce Step
        # Fallback to mock summary if Anthropic API key is not present
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "dummy-key":
            mock_summary = (
                "Tata Consultancy Services (TCS) demonstrated solid performance for the fiscal year 2023, "
                "driven by strong demand in the BFSI sector, cloud migrations, and generative AI adoption. "
                "Despite macroeconomic uncertainties, operating margins remained resilient at 24.1%."
            )
            mock_highlights = [
                "Revenue reached 2,25,458 crore INR, showing 17.6% growth year-on-year.",
                "Operating Margin stood at 24.1%, and Net Income was 42,147 crore INR.",
                "BFSI remains the largest business segment vertical.",
                "Geopolitical tensions and tech talent competition identified as primary risks."
            ]
            return {
                "summary": mock_summary,
                "highlights": mock_highlights,
                "generated_at": generated_at
            }

        client = get_anthropic_client()
        system_prompt = (
            "You are a senior financial writer. You will be provided with summaries of different pages of an annual report.\n"
            "Produce two outputs:\n"
            "1. A consolidated high-level executive summary (2-3 paragraphs, professional tone).\n"
            "2. A list of 4-6 key highlights / bullet points.\n"
            "Format your output exactly as:\n"
            "SUMMARY: [consoldated summary text]\n"
            "HIGHLIGHTS:\n"
            "- [highlight 1]\n"
            "- [highlight 2] etc."
        )

        try:
            response = await client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=800,
                temperature=0.0,
                system=system_prompt,
                messages=[{"role": "user", "content": combined_summaries_text}]
            )
            raw_result = response.content[0].text.strip()
            
            # Parse output
            summary_part = ""
            highlights = []
            
            if "SUMMARY:" in raw_result and "HIGHLIGHTS:" in raw_result:
                parts = raw_result.split("HIGHLIGHTS:")
                summary_part = parts[0].replace("SUMMARY:", "").strip()
                highlight_lines = parts[1].strip().split("\n")
                for line in highlight_lines:
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        highlights.append(line[1:].strip())
                    elif line:
                        highlights.append(line)
            else:
                summary_part = raw_result
                # Fallback to splitting by sentence for highlights
                sentences = raw_result.split(". ")
                highlights = [s.strip() + "." for s in sentences[:4] if len(s.strip()) > 10]

            return {
                "summary": summary_part,
                "highlights": highlights,
                "generated_at": generated_at
            }

        except Exception as e:
            return {
                "summary": f"Error during consolidate summary: {str(e)}",
                "highlights": ["Error generating highlights"],
                "generated_at": generated_at
            }


summarizer_service = SummarizerService()
