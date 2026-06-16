#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Apply a saved JsonCssExtractionStrategy schema against a URL. Deterministic,
LLM-free, runnable in batch / cron / CI.

Usage:
  ./extract_with_schema.py <url> <schema.json> [output.json]

Example:
  ./extract_with_schema.py https://shop.example.com shop_schema.json products.json
"""

import asyncio
import json
import sys
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def extract(url: str, schema_path: Path, output_file: Path) -> dict | None:
    if not schema_path.exists():
        print(f"FAILED: schema not found: {schema_path}")
        print("Generate one with: ./generate_schema.py <url> \"<instruction>\"")
        return None

    schema = json.loads(schema_path.read_text())
    extraction_strategy = JsonCssExtractionStrategy(schema=schema, verbose=False)
    crawler_config = CrawlerRunConfig(extraction_strategy=extraction_strategy, wait_until="networkidle")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

    if not (result.success and result.extracted_content):
        print(f"FAILED: {result.error_message if result else 'unknown error'}")
        return None

    data = json.loads(result.extracted_content)
    output_file.write_text(json.dumps(data, indent=2))

    items = data if isinstance(data, list) else data.get(schema.get("name", "items"), [])
    print(f"OK: extracted {len(items)} item(s), written to {output_file}")
    if items:
        print("Sample (first item):")
        print(json.dumps(items[0], indent=2))
    return data


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    url = sys.argv[1]
    schema_path = Path(sys.argv[2])
    output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("extracted_data.json")
    data = asyncio.run(extract(url, schema_path, output_file))
    return 0 if data is not None else 1


if __name__ == "__main__":
    sys.exit(main())
