# Crawl4AI CLI Guide

Command-line interface for the Crawl4AI library. Pairs with [SDK Guide](sdk-guide.md) for programmatic use and the
deeper [Complete SDK Reference](complete-sdk-reference.md).

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Browser Configuration](#browser-configuration)
- [Crawler Configuration](#crawler-configuration)
- [Extraction Configuration](#extraction-configuration)
- [Advanced Features](#advanced-features)
- [LLM Q&A](#llm-qa)
- [Structured Data Extraction](#structured-data-extraction)
- [Content Filtering](#content-filtering)
- [Output Formats](#output-formats)
- [Complete Examples](#complete-examples)
- [Best Practices & Tips](#best-practices--tips)

---

## Installation

The Crawl4AI CLI (`crwl`) is installed automatically with the library:

```bash
pip install crawl4ai
crawl4ai-setup
```

---

## Basic Usage

The `crwl` command provides a simple interface to the Crawl4AI library:

```bash
# Basic crawling - returns markdown
crwl https://example.com

# Specify output format
crwl https://example.com -o markdown

# Verbose JSON output with cache bypass
crwl https://example.com -o json -v --bypass-cache

# See usage examples
crwl --example
```

**Quick Example - Advanced Usage:**

```bash
# Extract structured data using CSS schema
crwl "https://www.infoq.com/ai-ml-data-eng/" \
    -e docs/examples/cli/extract_css.yml \
    -s docs/examples/cli/css_schema.json \
    -o json
```

---

## Configuration

### Browser Configuration

Browser settings via YAML file or command line:

```yaml
# browser.yml
headless: true
viewport_width: 1280
user_agent_mode: "random"
verbose: true
ignore_https_errors: true
```

```bash
# Using config file
crwl https://example.com -B browser.yml

# Using direct parameters
crwl https://example.com -b "headless=true,viewport_width=1280,user_agent_mode=random"
```

**Key Parameters:**

| Parameter         | Description                    |
| ----------------- | ------------------------------ |
| `headless`        | Run without GUI (true/false)   |
| `viewport_width`  | Browser width in pixels        |
| `viewport_height` | Browser height in pixels       |
| `user_agent_mode` | "random" or specific UA string |

For all browser parameters:
[BrowserConfig Reference](complete-sdk-reference.md#1-browserconfig--controlling-the-browser).

### Crawler Configuration

Control crawling behavior:

```yaml
# crawler.yml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 30000
delay_before_return_html: 0.5
word_count_threshold: 100
scan_full_page: true
scroll_delay: 0.3
process_iframes: false
remove_overlay_elements: true
magic: true
verbose: true
```

```bash
# Using config file
crwl https://example.com -C crawler.yml

# Using direct parameters
crwl https://example.com -c "css_selector=#main,delay_before_return_html=2,scan_full_page=true"
```

**Key Parameters:**

| Parameter        | Description                     |
| ---------------- | ------------------------------- |
| `cache_mode`     | bypass, enabled, disabled       |
| `wait_until`     | networkidle, domcontentloaded   |
| `page_timeout`   | Max page load time (ms)         |
| `css_selector`   | Focus on specific element       |
| `scan_full_page` | Enable infinite scroll handling |

For all crawler parameters:
[CrawlerRunConfig Reference](complete-sdk-reference.md#2-crawlerrunconfig--controlling-each-crawl).

### Extraction Configuration

Two extraction types supported:

**1. CSS/XPath-based extraction:**

```yaml
# extract_css.yml
type: "json-css"
params:
  verbose: true
```

```json
// css_schema.json
{
  "name": "ArticleExtractor",
  "baseSelector": ".article",
  "fields": [
    {
      "name": "title",
      "selector": "h1.title",
      "type": "text"
    },
    {
      "name": "link",
      "selector": "a.read-more",
      "type": "attribute",
      "attribute": "href"
    }
  ]
}
```

**2. LLM-based extraction:**

```yaml
# extract_llm.yml
type: "llm"
provider: "openai/gpt-4"
instruction: "Extract all articles with their titles and links"
api_token: "your-token"
params:
  temperature: 0.3
  max_tokens: 1000
```

For extraction strategies: [Extraction Strategies](complete-sdk-reference.md#extraction-strategies).

---

## Advanced Features

### LLM Q&A

Ask questions about crawled content:

```bash
# Simple question
crwl https://example.com -q "What is the main topic discussed?"

# View content then ask questions
crwl https://example.com -o markdown  # See content first
crwl https://example.com -q "Summarize the key points"
crwl https://example.com -q "What are the conclusions?"

# Combined with advanced crawling
crwl https://example.com \
    -B browser.yml \
    -c "css_selector=article,scan_full_page=true" \
    -q "What are the pros and cons mentioned?"
```

**First-time setup:**

- Prompts for LLM provider and API token
- Saves configuration in `~/.crawl4ai/global.yml`
- Any LiteLLM-supported provider works; pick a current model identifier from
  [LiteLLM Providers](https://docs.litellm.ai/docs/providers). `ollama/*` providers need no token.

### Structured Data Extraction

```bash
# CSS-based extraction
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json

# LLM-based extraction (schema lives inside extract_llm.yml; no -s needed)
crwl https://example.com \
    -e extract_llm.yml \
    -o json
```

### Content Filtering

Filter content for relevance:

```yaml
# filter_bm25.yml (relevance-based)
type: "bm25"
query: "target content"
threshold: 1.0

# filter_pruning.yml (quality-based — no query; heuristic block pruning)
type: "pruning"
threshold: 0.48
threshold_type: "fixed"
```

```bash
crwl https://example.com -f filter_bm25.yml -o markdown-fit
```

For content filtering: [Content Processing](complete-sdk-reference.md#content-processing).

---

## Output Formats

| Format         | Flag                             | Description                          |
| -------------- | -------------------------------- | ------------------------------------ |
| `all`          | `-o all`                         | Full crawl result including metadata |
| `json`         | `-o json`                        | Extracted structured data            |
| `markdown`     | `-o markdown` or `-o md`         | Raw markdown output                  |
| `markdown-fit` | `-o markdown-fit` or `-o md-fit` | Filtered markdown                    |

---

## Complete Examples

**1. Basic Extraction:**

```bash
crwl https://example.com \
    -B browser.yml \
    -C crawler.yml \
    -o json
```

**2. Structured Data Extraction:**

```bash
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json \
    -v
```

**3. LLM Extraction with Filtering:**

```bash
crwl https://example.com \
    -B browser.yml \
    -e extract_llm.yml \
    -f filter_bm25.yml \
    -o json
```

**4. Interactive Q&A:**

```bash
# First crawl and view
crwl https://example.com -o markdown

# Then ask questions
crwl https://example.com -q "What are the main points?"
crwl https://example.com -q "Summarize the conclusions"
```

---

## Best Practices & Tips

1. **Configuration Management:**

- Keep common configurations in YAML files
- Use CLI parameters for quick overrides
- Store sensitive data (API tokens) in `~/.crawl4ai/global.yml`

1. **Performance Optimization:**

- Use `--bypass-cache` for fresh content
- Enable `scan_full_page` for infinite scroll pages
- Adjust `delay_before_return_html` for dynamic content

1. **Content Extraction:**

- Use CSS extraction for structured content (faster, no API costs)
- Use LLM extraction for unstructured content
- Combine with filters for focused results

1. **Q&A Workflow:**

- View content first with `-o markdown`
- Ask specific questions
- Use broader context with appropriate selectors

---

## Recap

The Crawl4AI CLI provides:

- Flexible configuration via files and parameters
- Multiple extraction strategies (CSS, XPath, LLM)
- Content filtering and optimization
- Interactive Q&A capabilities
- Various output formats

---

## See Also

- [Python SDK Guide](sdk-guide.md) - Programmatic Python interface
- [Complete SDK Reference](complete-sdk-reference.md) - Full API documentation
- [Escalation](escalation.md) - What to do when an unknown flag, an empty extraction, or a version-drift surface
  surprises you
