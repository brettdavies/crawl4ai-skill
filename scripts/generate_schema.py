#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Generate a reusable JsonCssExtractionStrategy schema by asking an LLM to inspect
a sample page. One-time LLM cost; the produced schema then runs LLM-free via
`extract_with_schema.py`.

Usage:
  ./generate_schema.py <url> "<extract instruction>" [output_path]

Example:
  ./generate_schema.py https://shop.example.com "products with name, price, image" shop_schema.json

Output:
  Writes the JSON schema to <output_path> (default: generated_schema.json).
"""

import asyncio
import json
import sys
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy


async def generate_schema(url: str, instruction: str, output_file: Path) -> dict | None:
    print(f"Inspecting {url} with LLM to derive an extraction schema...")

    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        instruction=f"""
        Analyse this webpage and emit a CSS-based extraction schema as JSON.
        Task: {instruction}

        Required shape:
        {{
          "name": "items",
          "baseSelector": "<css selector for each item>",
          "fields": [
            {{"name": "field_name", "selector": "<relative selector>", "type": "text"}},
            {{"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}}
          ]
        }}

        Selectors must be specific enough to avoid false matches. Return only the JSON.
        """,
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
        schema = json.loads(result.extracted_content)
    except json.JSONDecodeError as e:
        print(f"FAILED: LLM did not return JSON: {e}")
        print("Raw output:", result.extracted_content[:500])
        return None

    if "fields" not in schema or "baseSelector" not in schema:
        print("WARNING: schema missing required keys; review before reuse.")

    output_file.write_text(json.dumps(schema, indent=2))
    print(f"OK: schema written to {output_file}")
    print(json.dumps(schema, indent=2))
    return schema


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    url = sys.argv[1]
    instruction = sys.argv[2]
    output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("generated_schema.json")
    schema = asyncio.run(generate_schema(url, instruction, output_file))
    return 0 if schema is not None else 1


if __name__ == "__main__":
    sys.exit(main())
