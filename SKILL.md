---
name: crawl4ai
description: Use when scraping JavaScript-heavy pages or SPAs, crawling multiple URLs concurrently, extracting structured data with reusable CSS/JSON schemas, or building automated web data pipelines. Wraps the Crawl4AI library (`crwl` CLI and Python SDK) with schema-generation patterns for LLM-free extraction. Triggers on crawl4ai, crwl, scrape JS-heavy site, scrape SPA, headless browser scrape, schema-based extraction, batch crawl, sitemap crawl, web data pipeline. SKIP when a static HTML page can be read with `defuddle` / `fetch-web` — those are faster cold-start and don't need a browser.
argument-hint: "[url]"
---

# Crawl4AI

**Verified against `crawl4ai`** [`VERSION`](VERSION). PEP 723 pins in `scripts/*.py` and `tests/*.py` floor at that
version.

## Overview

Crawl4AI wraps a headless browser (Playwright) plus a markdown-aware content pipeline. Use it when defuddle/curl can't
reach the content — JavaScript-rendered pages, login-gated content, infinite scroll, multi-URL concurrency, repeatable
schema-based extraction.

This skill exposes both interfaces of the underlying library:

- **CLI** (`crwl`) — quick, scriptable commands: [CLI Guide](references/cli-guide.md)
- **Python SDK** — full programmatic control: [SDK Guide](references/sdk-guide.md)

## Invoked with a URL argument

When the user runs `/crawl4ai <url>` with a single URL and no further qualifier, treat it as the JS-heavy fetch case and
default to:

```bash
crwl <url> -c "wait_until=networkidle,page_timeout=60000" -o markdown
```

`wait_until=networkidle` waits for the network to be quiet for ~500ms post-load — the right default when the user hasn't
named a specific element on a JS-rendered page. (Avoid `wait_for=css:body`: `<body>` exists at t=0 on every HTML
response, so it's satisfied before JS renders content.) Then return the markdown to the agent context. Adjust to
`wait_for=css:<selector>` if the user named a specific element. Skip the default and route to the relevant section below
for any task that names extraction, batch / multi-URL, login / session, screenshot / PDF, or URL discovery — those each
have their own pipeline. If the URL is clearly static (a docs page, a blog post), route the user to `/fetch-web` instead
per the "When NOT to use" section below.

## When NOT to use this skill

- **Static HTML pages** (most documentation sites, blog posts, news articles, tweets) — use `/fetch-web` or `defuddle`
  directly. Static extraction is ~0ms cold start; crawl4ai pays a ~2s browser startup tax.
- **Local file conversion** (`.pdf`, `.docx`, `.pptx`, `.epub`) — use `/markdown-convert`.
- **One-URL agent-context reads** (the agent just needs to read this page) — use `/fetch-web` and let it route to
  `defuddle`.
- **Mutating UI flows** (form fills, multi-step clicks, login + navigation) — `/browse` (gstack's persistent headless
  Chromium) is built for that.

## When stuck

For unknown crwl/SDK flags, scrape failures, or extraction edge cases the references don't cover, see
[references/escalation.md](references/escalation.md) for the lookup order (qmd solutions → upstream docs → GitHub issues
→ ask the user) and worked examples.

---

## Quick Start

### Installation

```bash
pip install crawl4ai
crawl4ai-setup

# Verify installation
crawl4ai-doctor
```

### CLI (Recommended)

```bash
# Basic crawling - returns markdown
crwl https://example.com

# Get markdown output
crwl https://example.com -o markdown

# JSON output with cache bypass
crwl https://example.com -o json -v --bypass-cache

# See more examples
crwl --example
```

### Python SDK

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])

asyncio.run(main())
```

For SDK configuration details: [SDK Guide - Configuration](references/sdk-guide.md#configuration).

---

## Core Concepts

### Configuration Layers

Both CLI and SDK use the same underlying configuration:

| Concept          | CLI                                    | SDK                       |
| ---------------- | -------------------------------------- | ------------------------- |
| Browser settings | `-B browser.yml` or `-b "param=value"` | `BrowserConfig(...)`      |
| Crawl settings   | `-C crawler.yml` or `-c "param=value"` | `CrawlerRunConfig(...)`   |
| Extraction       | `-e extract.yml -s schema.json`        | `extraction_strategy=...` |
| Content filter   | `-f filter.yml`                        | `markdown_generator=...`  |

### Key Parameters

**Browser Configuration:**

- `headless`: Run with/without GUI
- `viewport_width/height`: Browser dimensions
- `user_agent`: Custom user agent
- `proxy_config`: Proxy settings

**Crawler Configuration:**

- `page_timeout`: Max page load time (ms)
- `wait_for`: CSS selector or JS condition to wait for
- `cache_mode`: bypass, enabled, disabled
- `js_code`: JavaScript to execute
- `css_selector`: Focus on specific element

For complete parameters: [CLI Config](references/cli-guide.md#configuration) |
[SDK Config](references/sdk-guide.md#configuration)

### Output Content

Every crawl returns:

- **markdown** - Clean, formatted markdown
- **html** - Raw HTML
- **links** - Internal and external links discovered
- **media** - Images, videos, audio found
- **extracted_content** - Structured data (if extraction configured)

---

## Markdown Generation (Primary Use Case)

Crawl4AI excels at generating clean, well-formatted markdown.

### CLI

```bash
crwl https://docs.example.com -o markdown                              # raw markdown
crwl https://docs.example.com -o markdown-fit                          # filtered (noise removed)
crwl https://docs.example.com -f templates/filter_bm25.yml -o markdown-fit   # BM25-relevance filter
crwl https://docs.example.com -f templates/filter_pruning.yml -o markdown-fit # quality-based filter
```

Filter templates: [`templates/filter_bm25.yml`](templates/filter_bm25.yml) (relevance-scored against a query),
[`templates/filter_pruning.yml`](templates/filter_pruning.yml) (no query, prunes low-quality blocks).

### Python SDK

```python
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

bm25_filter = BM25ContentFilter(user_query="machine learning", bm25_threshold=1.0)
md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)

config = CrawlerRunConfig(markdown_generator=md_generator)
result = await crawler.arun(url, config=config)

print(result.markdown.fit_markdown)  # Filtered
print(result.markdown.raw_markdown)  # Original
```

For filter selection and config field reference, see [Content Filters](references/content-filters.md).

---

## Data Extraction

### 1. Schema-Based CSS Extraction (Most Efficient)

**No LLM required** at extract time — fast, deterministic, cost-free. One-time LLM cost to derive the schema, then reuse
indefinitely. The bundled scripts split the pipeline by responsibility:

```bash
./scripts/generate_schema.py https://shop.example.com "products with name, price, image" shop_schema.json
./scripts/extract_with_schema.py https://shop.example.com shop_schema.json products.json
```

Or via the CLI with the YAML strategy template + the saved schema:

```bash
crwl https://shop.example.com -e templates/extract_css.yml -s shop_schema.json -o json
```

Schema skeleton: [`templates/css_schema.json`](templates/css_schema.json). Strategy YAML:
[`templates/extract_css.yml`](templates/extract_css.yml).

### 2. LLM-Based Extraction

For one-off / irregular content where a CSS schema is too brittle:

```bash
./scripts/extract_with_llm.py https://news.example.com "Extract headlines, dates, summaries" news.json
```

Or via the CLI with the strategy template:

```bash
crwl https://news.example.com -e templates/extract_llm.yml -o json
```

Strategy YAML: [`templates/extract_llm.yml`](templates/extract_llm.yml). Pays an LLM call per URL — for repeat
extraction, prefer the schema pipeline above.

For extraction strategy reference: [Extraction Strategies](references/complete-sdk-reference.md#extraction-strategies).

---

## Advanced Patterns

### Dynamic Content (JavaScript-Heavy Sites)

```bash
crwl https://example.com -c "wait_for=css:.ajax-content,scan_full_page=true,page_timeout=60000"
crwl https://example.com -C templates/crawler.yml                          # all options in a YAML file
```

Crawler config template: [`templates/crawler.yml`](templates/crawler.yml).

### Multi-URL Processing

```bash
./scripts/batch_crawl.py urls.txt --max-concurrent 5 --out batch_markdown/
./scripts/batch_extract.py urls.txt shop_schema.json --max-concurrent 5 --out products.json
```

The two scripts split on responsibility: `batch_crawl.py` returns markdown per URL; `batch_extract.py` returns
schema-extracted JSON per URL. Python equivalent uses `arun_many()`:

```python
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = await crawler.arun_many(urls, config=config)
```

For batch processing reference: [arun_many() Reference](references/complete-sdk-reference.md#arunmany-reference).

### URL Discovery Before Crawl

When the URL list comes from a sitemap / domain rather than a known list, do discovery first, then feed the result into
`batch_crawl.py` / `batch_extract.py`. See [URL Discovery](references/url-discovery.md) for the full surface; quick
shape:

```python
from crawl4ai import AsyncUrlSeeder, SeedingConfig
seeds = await AsyncUrlSeeder().urls("example.com", SeedingConfig(
    source="sitemap+cc", pattern="*/blog/*", query="machine learning", score_threshold=0.3, live_check=True,
))
urls = [s["url"] for s in seeds]
```

`AsyncUrlSeeder` is best when you want BM25-scored filtering against a query; `DomainMapper` is best when you want
maximum coverage of one domain.

### Session & Authentication

Fill the login template, then reuse the session id on subsequent crawls:

```bash
crwl https://site.com/login -C templates/login_crawler.yml
crwl https://site.com/protected -c "session_id=user_session"
```

Login template: [`templates/login_crawler.yml`](templates/login_crawler.yml) (fill in the field-id selectors and the
post-login wait condition before use).

For session management reference: [Advanced Features](references/complete-sdk-reference.md#advanced-features).

### Anti-Detection & Proxies

```bash
crwl https://example.com -B templates/browser.yml
```

Browser config template: [`templates/browser.yml`](templates/browser.yml) (uncomment `proxy_config` and `init_scripts`
as needed). For pre-page-load script injection (fingerprint patches that must fire **before** any site script), populate
`init_scripts:` rather than `js_code:` (which fires after the page loads). `proxy_config` works with both the browser
strategy and the non-browser `HTTPCrawlerStrategy` — the latter is the cheap path for static fetches behind a corporate
proxy.

Full surface (CDP attachment, undetected mode, init script patterns): [Anti-Detection](references/anti-detection.md).

### Rendering Cached HTML (`raw:` / `file://`)

If the agent already has HTML in hand (e.g., from `defuddle` or a previous crawl) and only needs a screenshot, PDF, or
MHTML render, skip the network fetch and pass the HTML directly. `base_url` controls relative-link resolution:

```python
result = await crawler.arun(
    url="raw:" + html_string,
    config=CrawlerRunConfig(base_url="https://example.com", screenshot=True, pdf=True),
)
```

```python
result = await crawler.arun(
    url="file:///path/to/page.html",
    config=CrawlerRunConfig(screenshot=True),
)
```

---

## Common Use Cases

Eight worked end-to-end flows (docs page, JS-heavy SPA, e-commerce product extraction, news aggregation, topic-bound
domain crawl, login-required content, render existing HTML, Q&A) live in [Recipes](references/recipes.md). Pick the
recipe closest to the task at hand and adapt.

---

## Resources

### Provided Scripts

| Script                                               | Responsibility                                       |
| ---------------------------------------------------- | ---------------------------------------------------- |
| `scripts/basic_crawler.py <url>`                     | One URL → markdown + screenshot                      |
| `scripts/batch_crawl.py <urls.txt>`                  | Many URLs → markdown files                           |
| `scripts/batch_extract.py <urls.txt> <schema.json>`  | Many URLs + schema → JSON                            |
| `scripts/generate_schema.py <url> "<instruction>"`   | Derive a reusable CSS schema (one-time LLM call)     |
| `scripts/extract_with_schema.py <url> <schema.json>` | Apply a saved schema (no LLM)                        |
| `scripts/extract_with_llm.py <url> "<instruction>"`  | Per-request LLM extraction (expensive; one-off only) |

### Templates

YAML and JSON skeletons users copy and fill. All sit at the skill root under `templates/`:

| Template                       | Used for                                                    |
| ------------------------------ | ----------------------------------------------------------- |
| `templates/browser.yml`        | `BrowserConfig` (headless, proxy, user agent, init scripts) |
| `templates/crawler.yml`        | `CrawlerRunConfig` (cache, wait, timeout, JS)               |
| `templates/extract_css.yml`    | `JsonCssExtractionStrategy` declaration                     |
| `templates/extract_llm.yml`    | `LLMExtractionStrategy` declaration                         |
| `templates/filter_bm25.yml`    | BM25 content filter (relevance-scored)                      |
| `templates/filter_pruning.yml` | Pruning content filter (quality-based, no query)            |
| `templates/login_crawler.yml`  | Session-establishing login flow                             |
| `templates/css_schema.json`    | CSS schema skeleton                                         |

### Reference Documentation

| Document                                                       | Purpose                                                         |
| -------------------------------------------------------------- | --------------------------------------------------------------- |
| [CLI Guide](references/cli-guide.md)                           | Command-line interface reference                                |
| [SDK Guide](references/sdk-guide.md)                           | Python SDK quick reference                                      |
| [Recipes](references/recipes.md)                               | Eight worked end-to-end flows                                   |
| [URL Discovery](references/url-discovery.md)                   | `AsyncUrlSeeder`, `SeedingConfig`, `DomainMapper`               |
| [Content Filters](references/content-filters.md)               | BM25 vs Pruning vs LLMContentFilter — when to use which         |
| [Anti-Detection](references/anti-detection.md)                 | `init_scripts`, `proxy_config`, undetected mode, CDP attachment |
| [Troubleshooting](references/troubleshooting.md)               | Symptoms, causes, fixes; what to try before escalating          |
| [Complete SDK Reference](references/complete-sdk-reference.md) | Full API documentation (5900+ lines)                            |
| [Escalation](references/escalation.md)                         | Lookup order, iron rule, halt-vs-continue, worked examples      |

### Related learnings

-
  [`docs/solutions/developer-experience/skill-version-spdx-and-upstream-mirror-provenance.md`](../docs/solutions/developer-experience/skill-version-spdx-and-upstream-mirror-provenance.md)
  is the worked precedent for this skill's `VERSION` banner, per-file SPDX headers, and pinned-SHA upstream-mirror
  convention. Read that doc when refreshing the version pin, adding new bundled scripts/templates, or refreshing
  `references/complete-sdk-reference.md` from upstream.

---

## Best Practices

1. **Start with CLI** for quick tasks, SDK for automation
2. **Use schema-based extraction** - 10-100x more efficient than LLM
3. **Enable caching during development** - `--bypass-cache` only when needed
4. **Set appropriate timeouts** - 30s normal, 60s+ for JS-heavy sites
5. **Use content filters** for cleaner, focused markdown
6. **Respect rate limits** - Add delays between requests

---

## Troubleshooting

For symptom → cause → fix tables (JS not loading, bot detection, empty extracted content, session not persisting, slow
crawl, schema generation nonsense, post-upgrade regressions), see [Troubleshooting](references/troubleshooting.md). For
unknown surface the references don't cover, follow [Escalation](references/escalation.md).

---

For comprehensive API documentation, see [Complete SDK Reference](references/complete-sdk-reference.md).

## License

Dual-licensed under [MIT](LICENSE-MIT) OR [Apache-2.0](LICENSE-APACHE) at your option (SPDX: `MIT OR Apache-2.0`). See
[LICENSE](LICENSE) for the explainer + the carve-out for the upstream-mirrored `references/complete-sdk-reference.md`.
