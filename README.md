# Crawl4AI Agent Skill

Scrape JavaScript-heavy sites and extract structured data via reusable CSS schemas. A portable agent skill that wraps
the [Crawl4AI](https://crawl4ai.com/) CLI and Python SDK, written in the Anthropic SKILL.md format and consumable by any
agent host that loads SKILL.md-format bundles (Claude Code, Codex, Cursor, OpenCode, Cline, and others).

Verified against Crawl4AI library version `0.8.9` (pinned in [`VERSION`](VERSION)).

## Features

- **JS-aware crawling**: full headless-browser rendering with `wait_until=networkidle` defaults
- **Schema-based extraction**: derive a CSS selector schema once via LLM, apply it forever with no further LLM cost
- **LLM extraction**: per-request structured extraction when a schema is not worth deriving
- **Content filtering**: BM25 relevance filter and quality-based pruning, plain markdown or markdown-fit output
- **Concurrent batch crawling**: multi-URL processing with per-job concurrency caps
- **Session management**: persistent sessions for authenticated, multi-step flows
- **CLI and SDK**: both the `crwl` command-line tool and the `crawl4ai` Python SDK

## Installation

Clone the repo into the skills directory your agent host loads from:

```bash
# Claude Code
git clone https://github.com/brettdavies/crawl4ai-skill.git ~/.claude/skills/crawl4ai
```

For other agent hosts (Codex, Cursor, OpenCode, Cline, custom agents), clone into whichever directory your host scans
for SKILL.md-format bundles. Refer to your host's documentation for the skills directory location. The bundle root
contains `SKILL.md`, so the skill registers automatically once the directory is on the host's skills search path.

## Prerequisites

The skill calls into the Crawl4AI Python library, which must be installed in the runtime your agent uses:

```bash
pip install crawl4ai
crawl4ai-setup
crawl4ai-doctor
```

`crawl4ai-doctor` validates the install and confirms a headless browser is available.

## Quick start

CLI:

```bash
crwl https://example.com -c "wait_until=networkidle,page_timeout=60000" -o markdown
crwl https://example.com -o json -v --bypass-cache
```

Python SDK:

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])

asyncio.run(main())
```

## Bundle layout

| Path                                       | Contents                                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `SKILL.md`                                 | Entry point: trigger conditions, defaults, routing to specialized pipelines                            |
| `references/`                              | Nine reference guides for CLI, SDK, extraction, filtering, anti-detection, URL discovery, escalation   |
| `scripts/`                                 | Six PEP 723 helper scripts for crawl / extract / batch workflows                                       |
| `templates/`                               | Reusable YAML/JSON templates for browser, crawler, filters, and extraction strategies                  |
| `evals/`                                   | Four eval scenarios for verifying skill behavior end-to-end                                            |
| `fixtures/`                                | Schema-generation reference fixture (sample HTML, expected schema, expected JSON output)               |
| `tests/`                                   | Pytest suite covering basic crawling, markdown generation, extraction, advanced patterns, and fixtures |
| `VERSION`                                  | Pinned Crawl4AI library version the skill is verified against                                          |
| `LICENSE-APACHE`, `LICENSE-MIT`, `LICENSE` | Dual license texts and summary (SPDX `MIT OR Apache-2.0`)                                              |

## Documentation

- [SKILL.md](SKILL.md): complete skill documentation with examples
- [CLI Guide](references/cli-guide.md): command-line interface reference
- [SDK Guide](references/sdk-guide.md): Python SDK quick reference
- [Complete SDK Reference](references/complete-sdk-reference.md): full API documentation (5900+ lines)
- [Recipes](references/recipes.md): end-to-end task recipes (login flow, sitemap crawl, paginated extraction)
- [Content Filters](references/content-filters.md): BM25 vs pruning vs LLMContentFilter trade-offs
- [URL Discovery](references/url-discovery.md): sitemap, robots.txt, link-graph traversal
- [Anti-Detection](references/anti-detection.md): init scripts, proxy config, undetected mode, CDP attachment
- [Troubleshooting](references/troubleshooting.md): symptoms, causes, fixes
- [Escalation](references/escalation.md): lookup order, halt-vs-continue criteria, worked examples

## Common use cases

### Documentation to markdown

```bash
crwl https://docs.example.com -o markdown > docs.md
```

### E-commerce product monitoring

```bash
# Derive the schema once (uses LLM)
./scripts/generate_schema.py https://shop.example.com "products with name, price, image" shop_schema.json

# Apply the saved schema (no LLM cost per request)
./scripts/extract_with_schema.py https://shop.example.com shop_schema.json products.json
```

### News aggregation with relevance filtering

```bash
for url in news1.com news2.com news3.com; do
  crwl "https://$url" -f templates/filter_bm25.yml -o markdown-fit
done
```

## Scripts

| Script                                               | Purpose                                              |
| ---------------------------------------------------- | ---------------------------------------------------- |
| `scripts/basic_crawler.py <url>`                     | One URL → markdown + screenshot                      |
| `scripts/batch_crawl.py <urls.txt>`                  | Many URLs → markdown files                           |
| `scripts/batch_extract.py <urls.txt> <schema.json>`  | Many URLs + schema → JSON                            |
| `scripts/generate_schema.py <url> "<instruction>"`   | Derive a reusable CSS schema (one-time LLM call)     |
| `scripts/extract_with_schema.py <url> <schema.json>` | Apply a saved schema (no LLM)                        |
| `scripts/extract_with_llm.py <url> "<instruction>"`  | Per-request LLM extraction (expensive; one-off only) |

## Testing

```bash
cd tests
python run_all_tests.py
```

## License

Dual-licensed under Apache License 2.0 ([LICENSE-APACHE](LICENSE-APACHE)) or MIT License ([LICENSE-MIT](LICENSE-MIT)) at
your option. SPDX identifier: `MIT OR Apache-2.0`. See [LICENSE](LICENSE) for the full notice.

## Contributing

Contributions welcome. Open a pull request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
