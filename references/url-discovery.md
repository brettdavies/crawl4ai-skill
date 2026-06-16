# URL Discovery

Find URLs before crawling them. Two surfaces, picked by the shape of the question.

| Surface                            | Use when                                                                                        |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- |
| `AsyncUrlSeeder` + `SeedingConfig` | You have a query / topic and want BM25-scored URL relevance, with optional live HEAD validation |
| `DomainMapper`                     | You want maximum URL coverage of one domain, optionally including subdomains                    |

The output is a list of URLs that you feed into `arun_many()`, `batch_crawl.py`, or `batch_extract.py`. Discovery itself
never fetches page content.

## AsyncUrlSeeder

Discovers URLs from sitemaps and the Common Crawl index, applies pattern filters, scores by BM25 against a query, and
optionally validates each candidate with a live HEAD request before returning.

```python
from crawl4ai import AsyncUrlSeeder, SeedingConfig

config = SeedingConfig(
    source="sitemap+cc",        # "sitemap" | "cc" | "sitemap+cc"
    pattern="*/blog/*",         # glob filter on URL path
    query="machine learning",   # BM25 relevance scoring
    score_threshold=0.3,        # drop seeds below this score
    live_check=True,            # HEAD-validate each URL before returning
    max_concurrent=10,
)

seeder = AsyncUrlSeeder()
seeds = await seeder.urls("example.com", config)
urls = [s["url"] for s in seeds]
```

Each entry in `seeds` is a dict with `url`, `score` (BM25 0-1), and metadata pulled from sitemap entries / JSON-LD /
Open Graph tags (when available).

### SeedingConfig fields

| Field                      | Type       | Default     | Notes                                                                 |
| -------------------------- | ---------- | ----------- | --------------------------------------------------------------------- |
| `source`                   | str        | `"sitemap"` | `"sitemap"`, `"cc"`, or `"sitemap+cc"`                                |
| `pattern`                  | str / list | `None`      | Glob pattern(s) on URL path; matching mode controlled by `match_mode` |
| `query`                    | str        | `None`      | BM25 relevance score against page metadata; omit to skip scoring      |
| `score_threshold`          | float      | `0.0`       | Drop seeds below this BM25 score (only applies when `query` is set)   |
| `live_check`               | bool       | `False`     | HEAD-validate each URL; expensive but removes dead links              |
| `max_concurrent`           | int        | 10          | Concurrent HEAD requests when `live_check=True`                       |
| `cache_ttl_hours`          | int        | 24          | TTL for cached discovery results                                      |
| `validate_sitemap_lastmod` | bool       | `False`     | Re-fetch sitemap when `<lastmod>` indicates updates                   |

### Multi-domain parallel discovery

`AsyncUrlSeeder.many_urls()` runs discovery across multiple domains in parallel and returns the merged result. Use when
the URL universe spans more than one domain (e.g. a news aggregator).

```python
domains = ["site1.com", "site2.com", "site3.com"]
all_seeds = await seeder.many_urls(domains, config)
```

## DomainMapper

Comprehensive domain URL discovery. Walks sitemap + light crawl, optionally expands into subdomains, with a per-source
timeout so a slow sitemap doesn't block the whole map. Use when coverage is the goal and relevance scoring is not.

```python
from crawl4ai import DomainMapper

mapper = DomainMapper(
    include_subdomains=False,   # True to walk `*.example.com`
    per_source_timeout=30,      # seconds per discovery source
)
urls = await mapper.map_domain("example.com")
```

Returns a flat list of URLs deduplicated across sources. Pair with `arun_many()` for the actual crawl.

## When to pick which

- **Topic-bound and high-precision**: `AsyncUrlSeeder` with `query` + `score_threshold`. Best for "I want all blog posts
  about X."
- **Domain-bound and high-recall**: `DomainMapper`. Best for "give me every URL on this site."
- **Both**: run `DomainMapper` first, then filter the result with `AsyncUrlSeeder.urls(domain, config)` where `query`
  encodes the topic.

## Composition with the bundled scripts

```bash
# Discover, write to urls.txt, then batch-crawl
python -c "
import asyncio
from crawl4ai import AsyncUrlSeeder, SeedingConfig
async def main():
    s = AsyncUrlSeeder()
    seeds = await s.urls('example.com', SeedingConfig(source='sitemap+cc', query='ml', score_threshold=0.3))
    for x in seeds: print(x['url'])
asyncio.run(main())
" > urls.txt

./scripts/batch_crawl.py urls.txt --out batch_markdown/
./scripts/batch_extract.py urls.txt my_schema.json --out batch_extracted.json
```

The seeder + mapper APIs are documented in detail in [`complete-sdk-reference.md`](complete-sdk-reference.md). When the
field names here diverge from the installed library, verify against the installed version (`crwl --version` or `python
-c "import importlib.metadata; print(importlib.metadata.version('crawl4ai'))"`) and the `VERSION` file at the skill
root. When stuck, see [escalation.md](escalation.md) for the full lookup order.
