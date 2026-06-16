#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Apply a saved JsonCssExtractionStrategy schema across many URLs concurrently.
For markdown-only batch crawls (no schema), use `batch_crawl.py` instead.

Usage:
  ./batch_extract.py <urls.txt | url1,url2,...> <schema.json> [--max-concurrent N] [--out FILE]

Example:
  ./batch_extract.py shop_urls.txt shop_schema.json --max-concurrent 5 --out products.json
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


def load_urls(source: str) -> List[str]:
    p = Path(source)
    if p.exists():
        out = []
        for line in p.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                out.append(stripped)
        return out
    return [u.strip() for u in source.split(",") if u.strip()]


async def batch_extract(urls: List[str], schema: dict, max_concurrent: int, out_file: Path) -> list:
    print(f"Batch extracting {len(urls)} URL(s) with schema '{schema.get('name', 'items')}'")

    extraction_strategy = JsonCssExtractionStrategy(schema=schema)
    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle",
    )

    extracted: list[dict] = []

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls=urls, config=crawler_config, max_concurrent=max_concurrent)

    for result in results:
        if result.success and result.extracted_content:
            try:
                data = json.loads(result.extracted_content)
                extracted.append({"url": result.url, "data": data})
                items = data if isinstance(data, list) else data.get(schema.get("name", "items"), [])
                print(f"OK   {result.url} ({len(items)} item(s))")
            except json.JSONDecodeError:
                print(f"FAIL {result.url}: extracted_content is not valid JSON")
        else:
            print(f"FAIL {result.url}: {result.error_message if result else 'unknown error'}")

    out_file.write_text(json.dumps(extracted, indent=2))
    print(f"\nSummary: {len(extracted)} URL(s) extracted, written to {out_file}")
    return extracted


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    urls = load_urls(sys.argv[1])
    if not urls:
        print("FAILED: no URLs found")
        return 1

    schema_path = Path(sys.argv[2])
    if not schema_path.exists():
        print(f"FAILED: schema not found: {schema_path}")
        return 1
    schema = json.loads(schema_path.read_text())

    max_concurrent = 5
    out_file = Path("batch_extracted.json")
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--max-concurrent" and i + 1 < len(args):
            max_concurrent = int(args[i + 1])
            i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_file = Path(args[i + 1])
            i += 2
        else:
            print(f"Unknown arg: {args[i]}")
            return 1

    asyncio.run(batch_extract(urls, schema, max_concurrent, out_file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
