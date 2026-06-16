#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Crawl a list of URLs concurrently and dump each as a markdown file. Use when
you have a known URL list and want markdown out fast. For schema-based field
extraction across many URLs, use `batch_extract.py` instead.

Usage:
  ./batch_crawl.py <urls.txt | url1,url2,...> [--max-concurrent N] [--out DIR]

Example:
  ./batch_crawl.py urls.txt --max-concurrent 5 --out batch_markdown
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


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


def safe_filename(url: str, max_len: int = 100) -> str:
    bare = url.replace("https://", "").replace("http://", "")
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in bare)[:max_len]


async def batch_crawl(urls: List[str], max_concurrent: int, out_dir: Path) -> dict:
    print(f"Batch crawling {len(urls)} URL(s), max {max_concurrent} concurrent")
    out_dir.mkdir(exist_ok=True, parents=True)

    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        remove_overlay_elements=True,
        wait_until="networkidle",
        page_timeout=30000,
        screenshot=False,
    )

    success: list[dict] = []
    failed: list[dict] = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls=urls, config=crawler_config, max_concurrent=max_concurrent)

    for i, result in enumerate(results):
        if result.success:
            title = result.metadata.get("title", result.url)
            file_path = out_dir / f"{i:03d}_{safe_filename(result.url)}.md"
            file_path.write_text(
                f"# {title}\n\nURL: {result.url}\n\n{result.markdown}"
            )
            success.append({"url": result.url, "title": title, "file": str(file_path)})
            print(f"OK   {result.url}")
        else:
            failed.append({"url": result.url, "error": result.error_message})
            print(f"FAIL {result.url}: {result.error_message}")

    summary = {"success_count": len(success), "failed_count": len(failed), "success": success, "failed": failed}
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\nSummary: {len(success)} OK, {len(failed)} failed. Markdown in {out_dir}/, summary in {out_dir}/_summary.json")
    return summary


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    urls = load_urls(sys.argv[1])
    if not urls:
        print("FAILED: no URLs found")
        return 1

    max_concurrent = 5
    out_dir = Path("batch_markdown")
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--max-concurrent" and i + 1 < len(args):
            max_concurrent = int(args[i + 1])
            i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_dir = Path(args[i + 1])
            i += 2
        else:
            print(f"Unknown arg: {args[i]}")
            return 1

    asyncio.run(batch_crawl(urls, max_concurrent, out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
