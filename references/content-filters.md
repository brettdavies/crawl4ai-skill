# Content Filters

The markdown generator can route through a content filter before producing `fit_markdown`. Three filter types, different
selection criteria.

| Filter                 | When to use                                                             | Cost              | Templates                                                         |
| ---------------------- | ----------------------------------------------------------------------- | ----------------- | ----------------------------------------------------------------- |
| `PruningContentFilter` | You want clean markdown without a topic. Quality-based block filtering. | Free              | [`templates/filter_pruning.yml`](../templates/filter_pruning.yml) |
| `BM25ContentFilter`    | You have a query / topic; want only relevant blocks. Lexical relevance. | Free              | [`templates/filter_bm25.yml`](../templates/filter_bm25.yml)       |
| `LLMContentFilter`     | The query is fuzzy and BM25 misses semantically related content.        | LLM call per page | n/a                                                               |

Every crawl returns both `result.markdown.raw_markdown` (always populated) and `result.markdown.fit_markdown` (populated
only when a filter is configured). When no filter is configured, `fit_markdown` is `None`.

## PruningContentFilter (default-good)

Removes low-quality blocks (boilerplate, navigation residue, short fragments) based on a heuristic score. No query
needed.

```python
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

pruning_filter = PruningContentFilter(
    threshold=0.48,           # 0.0 keeps everything, 1.0 prunes aggressively
    threshold_type="fixed",   # "fixed" or "dynamic"
)
md_generator = DefaultMarkdownGenerator(content_filter=pruning_filter)
config = CrawlerRunConfig(markdown_generator=md_generator)
```

`threshold_type="dynamic"` adjusts per-page based on content density; useful across heterogeneous corpora. Start with
`fixed` at `0.48` and tune up if too much boilerplate survives, down if real content disappears.

## BM25ContentFilter

Lexical relevance scoring against a query string. Blocks below `bm25_threshold` are dropped.

```python
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

bm25_filter = BM25ContentFilter(
    user_query="machine learning tutorials",
    bm25_threshold=1.0,       # higher = stricter
)
md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
```

BM25 is lexical, not semantic — it matches token overlap, weighted by IDF. It will miss "deep learning" when the query
is "neural networks" unless the page also uses that vocabulary. For semantic match, use `LLMContentFilter`.

## LLMContentFilter

LLM-judged relevance per block. Most expensive; use when:

- The query is conceptual and BM25 misses too much
- The page is long enough that the LLM cost is worth it vs scraping the noise
- You're piloting a corpus before settling on a cheaper filter

```python
from crawl4ai.content_filter_strategy import LLMContentFilter
from crawl4ai import LLMConfig

llm_filter = LLMContentFilter(
    llm_config=LLMConfig(provider="openai/gpt-4o-mini"),
    instruction="Keep only blocks discussing the company's revenue or growth metrics",
)
md_generator = DefaultMarkdownGenerator(content_filter=llm_filter)
```

## Filter selection heuristic

1. Try `PruningContentFilter` with `threshold=0.48`, `threshold_type="fixed"` first. If output looks clean, stop.
2. If output still contains topic-irrelevant content AND you have a query/topic, switch to `BM25ContentFilter` with
   `bm25_threshold=1.0`.
3. If BM25 over-prunes (real content scored low because vocabulary doesn't match), tune `bm25_threshold` down to ~0.5.
4. If after BM25 tuning the filter still misses semantically related content, switch to `LLMContentFilter` and
   acknowledge the per-page cost.

## CLI equivalents

Each Python filter has a YAML form for `crwl -f filter.yml`:

```bash
crwl https://docs.example.com -f templates/filter_bm25.yml -o markdown-fit
crwl https://docs.example.com -f templates/filter_pruning.yml -o markdown-fit
```

`LLMContentFilter` is SDK-only at the CLI level — `crwl` does not currently expose it as a YAML strategy. Use the Python
SDK when LLM-filtered markdown is required.

## Accessing both filtered and raw markdown

```python
result = await crawler.arun(url, config=config)
print(result.markdown.raw_markdown)   # always present
print(result.markdown.fit_markdown)   # filtered, or None if no filter
```

`raw_markdown` is useful as a fallback when the filter produces empty output (e.g. the threshold was too aggressive).
Log both during tuning.

## When stuck

For a filter constructor that raises on a kwarg this page doesn't name, or `fit_markdown` that comes back unexpectedly
empty, see [escalation.md](escalation.md) for the lookup order and worked examples.
