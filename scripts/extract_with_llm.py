#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Per-request LLM extraction. Most expensive approach (LLM call on every fetch);
use only for one-off / irregular content where a CSS schema is too brittle.
For repeated extractions, prefer:
  1. ./generate_schema.py to derive a schema (one LLM call)
  2. ./extract_with_schema.py to reuse it (no LLM calls)

Usage:
  ./extract_with_llm.py <url> "<extraction instruction>" [output.json]

Example:
  ./extract_with_llm.py https://news.example.com "Extract headlines, dates, summaries" news.json
"""

import asyncio
import json
import sys
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy


async def extract(url: str, instruction: str, output_file: Path) -> dict | None:
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        instruction=instruction,
        schema={
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "object"}},
                "summary": {"type": "string"},
            },
        },
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        wait_until="networkidle",
        remove_overlay_elements=True,
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

    if not (result.success and result.extracted_content):
        print(f"FAILED: {result.error_message if result else 'unknown error'}")
        return None

    try:
        data = json.loads(result.extracted_content)
    except json.JSONDecodeError:
        print("FAILED: LLM output is not valid JSON")
        print(result.extracted_content[:500])
        return None

    output_file.write_text(json.dumps(data, indent=2))
    items = data.get("items", [])
    print(f"OK: LLM extracted {len(items)} item(s), written to {output_file}")
    if data.get("summary"):
        print(f"Summary: {data['summary']}")
    if items:
        print("Sample (first item):")
        print(json.dumps(items[0], indent=2))
    return data


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    url = sys.argv[1]
    instruction = sys.argv[2]
    output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("llm_extracted.json")
    data = asyncio.run(extract(url, instruction, output_file))
    return 0 if data is not None else 1


if __name__ == "__main__":
    sys.exit(main())
