# Crawl4AI Skill Tests

Integration smoke tests that verify the skill's documented patterns still work against the installed `crawl4ai` library.
The patterns are surfaced in SKILL.md, with the deep reference in `references/` (cli-guide, sdk-guide, url-discovery,
content-filters, anti-detection, complete-sdk-reference). The tests cross-check the documented API surface, not the
prose of any particular reference file.

## Test files

| File                          | Coverage                                                                         |
| ----------------------------- | -------------------------------------------------------------------------------- |
| `test_basic_crawling.py`      | `BrowserConfig`, `CrawlerRunConfig`, `AsyncWebCrawler` smoke crawl               |
| `test_markdown_generation.py` | Default markdown, `BM25ContentFilter`, `PruningContentFilter`, generator options |
| `test_data_extraction.py`     | `JsonCssExtractionStrategy` manual schema, `LLMExtractionStrategy` constructor   |
| `test_advanced_patterns.py`   | `session_id` reuse, `proxy_config` shape, `arun_many` batch                      |
| `test_fixtures.py`            | Deterministic schema extraction against the bundled `fixtures/` pair             |

## Running

```bash
./run_all_tests.py                        # all tests, summary at end
./test_basic_crawling.py                  # any single test in isolation
./test_fixtures.py                        # the deterministic fixture pair
```

Every script is a self-contained PEP 723 (`uv run --script`) invocation; dependencies resolve on first run.

## Requirements

- `crawl4ai>=0.8.9` (matches the floor pin in `VERSION` and the script shebangs).
- The four integration tests reach `example.com` / `example.org`; network access required.
- `test_fixtures.py` is fully offline — it uses the `raw:` URL form against the bundled HTML.
- LLM-extraction test only verifies constructor shape; no API key needed.

## What "pass" means

A green run confirms:

- The documented API surface (class names, constructor kwargs, return shapes) still matches the installed library.
- The deterministic fixture still extracts the expected three product records.

A red run means one of the following — investigate in this order before bumping `VERSION`:

1. The installed library has drifted (e.g., a renamed field or a default behaviour change). Check the upstream
   `CHANGELOG.md` against the version currently in `VERSION`.
2. The fixture HTML or schema needs updating (rare; the fixture is intentionally stable).
3. A genuine regression in `crawl4ai`. Open an upstream issue.
