# Crawl4AI Claude Skill

A comprehensive Claude skill for web crawling and data extraction using Crawl4AI. This skill enables Claude to scrape websites, extract structured data, handle JavaScript-heavy pages, crawl multiple URLs, and build automated web data pipelines.

## Features

- **Web Crawling**: Extract content from any website with full JavaScript support
- **Data Extraction**: Schema-based CSS extraction (LLM-free) and LLM-based extraction
- **Markdown Generation**: Clean, well-formatted markdown output optimized for LLM consumption
- **Content Filtering**: Relevance-based filtering using BM25 and quality-based pruning
- **Session Management**: Persistent sessions for authenticated crawling
- **Batch Processing**: Concurrent multi-URL crawling
- **CLI & SDK**: Both command-line interface and Python SDK support

## Installation

### Method 1: Import as ZIP (Recommended for Claude Desktop)

1. Download or clone this repository
2. Create a ZIP file of the `crawl4ai` directory:

   ```bash
   cd crawl4ai-skill
   zip -r crawl4ai.zip crawl4ai/
   ```

3. In Claude Desktop, go to Settings → Developer → Import Skill
4. Select the `crawl4ai.zip` file

### Method 2: Git Clone

```bash
git clone https://github.com/brettdavies/crawl4ai-skill.git
cd crawl4ai-skill
```

Then add the skill directory to Claude's skills folder or import via Claude Desktop.

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

- **[SKILL.md](crawl4ai/SKILL.md)** - Complete skill documentation with examples
- **[CLI Guide](crawl4ai/references/cli-guide.md)** - Command-line interface reference
- **[SDK Guide](crawl4ai/references/sdk-guide.md)** - Python SDK quick reference
- **[Complete SDK Reference](crawl4ai/references/complete-sdk-reference.md)** - Full API documentation (5900+ lines)

## Common Use Cases

### Documentation to Markdown

```bash
crwl https://docs.example.com -o markdown > docs.md
```

### E-commerce Product Monitoring

```bash
# Generate schema once (uses LLM)
python crawl4ai/scripts/extraction_pipeline.py --generate-schema https://shop.com "extract products"

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

The skill includes helper scripts in `crawl4ai/scripts/`:

- **basic_crawler.py** - Simple markdown extraction
- **batch_crawler.py** - Multi-URL processing
- **extraction_pipeline.py** - Schema generation and extraction

## Testing

Run the test suite to verify the skill works correctly:

```bash
cd crawl4ai/tests
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
