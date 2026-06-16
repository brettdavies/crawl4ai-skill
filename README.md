# Crawl4AI Claude Skill

A comprehensive Claude skill for web crawling and data extraction using Crawl4AI. This skill enables Claude to scrape
websites, extract structured data, handle JavaScript-heavy pages, crawl multiple URLs, and build automated web data
pipelines.

## Features

- **Web Crawling**: Extract content from any website with full JavaScript support
- **Data Extraction**: Schema-based CSS extraction (LLM-free) and LLM-based extraction
- **Markdown Generation**: Clean, well-formatted markdown output optimized for LLM consumption
- **Content Filtering**: Relevance-based filtering using BM25 and quality-based pruning
- **Session Management**: Persistent sessions for authenticated crawling
- **Batch Processing**: Concurrent multi-URL crawling
- **CLI & SDK**: Both command-line interface and Python SDK support

## Installation

### Claude Code (load directly from a directory)

```bash
git clone https://github.com/brettdavies/crawl4ai-skill.git ~/.claude/skills/crawl4ai
```

Claude Code reads `SKILL.md` at the directory root.

### Claude Desktop (import a zip)

Claude Desktop expects the zip to contain a single top-level directory whose name matches the skill. Stage the skill
files under a `crawl4ai/` wrapper before zipping:

```bash
git clone https://github.com/brettdavies/crawl4ai-skill.git
cd crawl4ai-skill
mkdir -p /tmp/crawl4ai-pkg/crawl4ai
cp -r SKILL.md references scripts tests /tmp/crawl4ai-pkg/crawl4ai/
( cd /tmp/crawl4ai-pkg && zip -r crawl4ai.zip crawl4ai/ )
```

Then in Claude Desktop go to Settings → Developer → Import Skill and select `/tmp/crawl4ai-pkg/crawl4ai.zip`.

## Prerequisites

This skill requires the Crawl4AI Python library:

```bash
pip install crawl4ai
crawl4ai-setup

# Verify installation
crawl4ai-doctor
```

## Quick Start

### CLI Usage (Recommended for Quick Tasks)

```bash
# Basic crawling - returns markdown
crwl https://example.com

# Get markdown output
crwl https://example.com -o markdown

# JSON output with cache bypass
crwl https://example.com -o json -v --bypass-cache
```

### Python SDK Usage

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])

asyncio.run(main())
```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation with examples
- **[CLI Guide](references/cli-guide.md)** - Command-line interface reference
- **[SDK Guide](references/sdk-guide.md)** - Python SDK quick reference
- **[Complete SDK Reference](references/complete-sdk-reference.md)** - Full API documentation (5900+ lines)

## Common Use Cases

### Documentation to Markdown

```bash
crwl https://docs.example.com -o markdown > docs.md
```

### E-commerce Product Monitoring

```bash
# Generate schema once (uses LLM)
python scripts/extraction_pipeline.py --generate-schema https://shop.com "extract products"

# Use schema for extraction (no LLM costs)
crwl https://shop.com -e extract_css.yml -s product_schema.json -o json
```

### News Aggregation

```bash
# Multiple sources with filtering
for url in news1.com news2.com news3.com; do
  crwl "https://$url" -f filter_bm25.yml -o markdown-fit
done
```

## Scripts

The skill includes helper scripts in `scripts/`:

- **basic_crawler.py** - Simple markdown extraction
- **batch_crawler.py** - Multi-URL processing
- **extraction_pipeline.py** - Schema generation and extraction

## Testing

Run the test suite to verify the skill works correctly:

```bash
cd tests
python run_all_tests.py
```

## Marketplace

This skill is available on Claude Skills marketplaces:

- [Skills.pub](https://skills.pub/)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
