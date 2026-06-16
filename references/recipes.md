# Recipes — worked end-to-end flows

Each recipe is a complete walkthrough from "I have a URL" to "I have the data I wanted." Pick the one closest to your
situation and adapt.

## 1. One static documentation page → markdown file

Goal: clean markdown of a single docs page.

```bash
crwl https://docs.example.com/guide -o markdown > guide.md
```

If the page has navigation residue, add a pruning filter:

```bash
crwl https://docs.example.com/guide -f templates/filter_pruning.yml -o markdown-fit > guide.md
```

Pair with the [`/fetch-web` skill](../../fetch-web/SKILL.md) for static pages where browser cold-start is not worth
paying — `defuddle` returns ~0ms vs crawl4ai's ~2s.

## 2. A JS-heavy SPA → markdown

Goal: a Next.js / Vue / React app that doesn't render in `curl`.

```bash
crwl https://app.example.com -c "wait_for=css:.results,page_timeout=60000" -o markdown
```

If `wait_for=css:` times out, try a JS predicate:

```bash
crwl https://app.example.com -c "wait_for=js:document.querySelector('.results') !== null,page_timeout=60000"
```

For aggressive bot detection, layer `templates/browser.yml` (Layer 1: random UA) and `init_scripts` (Layer 2:
fingerprint patches) — see [Anti-Detection](anti-detection.md).

## 3. E-commerce product list across many URLs

Goal: extract `{name, price, link}` for products across many shop URLs.

```bash
# 1. Derive a schema from one URL (one LLM call)
./scripts/generate_schema.py https://shop.example.com/category "products with name, price, link" shop_schema.json

# 2. Sanity check the schema on a single page (no LLM)
./scripts/extract_with_schema.py https://shop.example.com/category shop_schema.json /tmp/check.json
jaq '.products[0:3]' /tmp/check.json

# 3. Run across the full URL list (no LLM, concurrent)
./scripts/batch_extract.py shop_urls.txt shop_schema.json --max-concurrent 5 --out products.json
```

If step 2 returns an empty list, the LLM-derived `baseSelector` doesn't match. Inspect the page HTML and adjust the
schema by hand (see
[Escalation example 2](escalation.md#example-2--jsoncssextractionstrategy-returns--despite-valid-schema)).

## 4. News aggregation by topic

Goal: collect markdown from many news sites, filtered by topic relevance.

```bash
# Per-source BM25-filtered markdown
for url in $(cat news_urls.txt); do
  slug=$(echo "$url" | sed 's|https://||; s|/|_|g')
  crwl "$url" -f templates/filter_bm25.yml -o markdown-fit > "news/$slug.md"
done
```

Edit `templates/filter_bm25.yml` to set the `query` to your topic before running. Tune `threshold` up if the filter
keeps too much noise.

For semantic relevance (e.g. when the topic vocabulary doesn't match the article's vocabulary), switch to
`LLMContentFilter` per [Content Filters § LLMContentFilter](content-filters.md#llmcontentfilter).

## 5. Topic-bound crawl of a single domain

Goal: every blog post on `example.com` about machine learning.

```bash
# 1. Discover URLs from sitemap + Common Crawl, BM25-filter by topic, validate live
python3 -c "
import asyncio, sys
from crawl4ai import AsyncUrlSeeder, SeedingConfig
async def main():
    seeds = await AsyncUrlSeeder().urls('example.com', SeedingConfig(
        source='sitemap+cc',
        pattern='*/blog/*',
        query='machine learning',
        score_threshold=0.3,
        live_check=True,
    ))
    for s in seeds:
        print(s['url'])
asyncio.run(main())
" > ml_urls.txt

# 2. Crawl them
./scripts/batch_crawl.py ml_urls.txt --out ml_markdown/
```

For maximum-coverage discovery (no query / topic), substitute `DomainMapper`:

```python
from crawl4ai import DomainMapper
urls = await DomainMapper(include_subdomains=False).map_domain("example.com")
```

See [URL Discovery](url-discovery.md) for the full surface.

## 6. Login-required content

Goal: scrape content behind a login.

```bash
# 1. Fill in templates/login_crawler.yml with selectors + post-login wait condition
# 2. Login (cookies persist under the session_id)
crwl https://site.com/login -C templates/login_crawler.yml

# 3. Access protected pages, reusing the session
crwl https://site.com/dashboard -c "session_id=user_session" -o markdown
crwl https://site.com/profile -c "session_id=user_session" -o markdown
```

For credentials: never inline them in `templates/login_crawler.yml`. Use environment variables and substitute at
invocation, or pass via a generated YAML file deleted after use.

## 7. Render existing HTML → screenshot / PDF

Goal: you already have HTML in hand (from `defuddle`, a previous crawl, or a database); only need crawl4ai's render.

```python
result = await crawler.arun(
    url="raw:" + html_string,
    config=CrawlerRunConfig(
        base_url="https://example.com",   # for relative-link resolution
        screenshot=True,
        pdf=True,
    ),
)
# result.screenshot is base64; result.pdf is bytes
```

For local files:

```python
result = await crawler.arun(
    url="file:///path/to/page.html",
    config=CrawlerRunConfig(screenshot=True),
)
```

This is the cheap path when the network fetch was already paid by another tool.

## 8. Q&A over a page

Goal: ask questions of crawled content via the LLM CLI.

```bash
crwl https://example.com -o markdown                          # preview
crwl https://example.com -q "What are the main conclusions?"  # ask
crwl https://example.com -q "Summarize in 3 bullets"
```

First-time setup prompts for the LLM provider and API token; stored in `~/.crawl4ai/global.yml`. Supports
`openai/gpt-4`, `anthropic/claude-3-sonnet`, and any LiteLLM-supported provider.
