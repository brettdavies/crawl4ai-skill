#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Runs the deterministic fixture pair in `fixtures/` end to end:

  1. Loads `fixtures/sample-products.html` (3 product cards).
  2. Loads `fixtures/sample-products-schema.json` (the CSS schema).
  3. Crawls the HTML via `raw:` URL with `JsonCssExtractionStrategy`.
  4. Diffs the result against `fixtures/sample-products-expected.json`.

A clean diff means the wrapper script + the installed library still produce
the documented output shape. A non-empty diff means either the library drifted
(scraping fidelity regression), the fixture HTML changed shape, or the schema
is wrong. Bump `VERSION` only after this passes against the new library
version.

Exit 0 on match, 1 on diff or library error.
"""

import asyncio
import json
import sys
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


async def run() -> int:
    html = (FIXTURES / "sample-products.html").read_text()
    schema = json.loads((FIXTURES / "sample-products-schema.json").read_text())
    expected = json.loads((FIXTURES / "sample-products-expected.json").read_text())

    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=strategy)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="raw:" + html, config=config)

    if not (result.success and result.extracted_content):
        print(f"FAIL: crawl did not produce extracted_content: {result.error_message}")
        return 1

    actual_raw = json.loads(result.extracted_content)
    # Library may return either a flat list OR a dict keyed by schema['name'].
    actual = actual_raw if isinstance(actual_raw, list) else actual_raw.get(schema["name"], [])

    if actual == expected:
        print(f"OK: fixture extraction matches expected ({len(actual)} item(s))")
        return 0

    print("FAIL: fixture extraction does not match expected output")
    print("Expected:")
    print(json.dumps(expected, indent=2))
    print("Actual:")
    print(json.dumps(actual, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
