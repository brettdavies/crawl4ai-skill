# When stuck — escalation guidance

The references in this skill cover the common cases the CLI and SDK are built around. When the question goes further —
an obscure `crwl` flag, an extraction strategy that returns empty, a Playwright timing edge case the docs don't name —
follow the lookup order below before guessing. Guessing about library API shape is the failure mode this section exists
to prevent.

## Iron rule — what NOT to guess about

**Never invent crawl4ai API surface from training data.** The skill is verified against the version recorded in
[`VERSION`](../VERSION); confirm against that version before committing to a name. Specifically: do not fabricate

- function/method names (`crawler.run`, `extract_json`, `set_proxy`, etc.) without confirming via
  `complete-sdk-reference.md` or upstream docs
- field names on `BrowserConfig`, `CrawlerRunConfig`, `LLMConfig`, `JsonCssExtractionStrategy`, or schema dicts
- CLI flags for `crwl` (use `crwl --help` and `crwl --example` to enumerate the real surface)
- content-filter constructor kwargs (`PruningContentFilter`, `BM25ContentFilter`, `LLMContentFilter`)
- output shape of `CrawlResult` (e.g. `result.markdown` is a `StringCompatibleMarkdown`, not a plain `str`)

**Carve-out — these are always fine without confirmation:**

- Running `crwl --help`, `crwl --example`, `crwl --version`
- Running `crawl4ai-doctor` to diagnose the local install
- Reading any file under this skill (SKILL.md, references, scripts, tests)
- Running `python -c "import importlib.metadata; print(importlib.metadata.version('crawl4ai'))"` (or `crwl --version`)
  to check the installed version. **Note:** `crawl4ai.__version__` is itself a module in 0.8.x, so the obvious
  `print(crawl4ai.__version__)` form prints the module repr, not the version string. Use `importlib.metadata.version`
  instead.
- Running the bundled `tests/` against `example.com` — they're read-only smoke checks

The prohibition is on inventing names; verifying via `--help`, reading source, or running a non-mutating probe never
qualifies.

## Lookup order

1. **`qmd query --collection solutions "<problem statement>"`** — the team's internal solutions corpus. Always first.
   Use 2-3 focused queries varying angle (e.g. "crawl4ai schema generation", "JsonCssExtractionStrategy empty output",
   "playwright wait_for selector timeout"). Most past gotchas with this library — version drift, schema constructors,
   filter combinations — have an entry there.
2. **This skill's references** — `cli-guide.md`, `sdk-guide.md`, `complete-sdk-reference.md` in that order. The complete
   reference is 5900+ lines; jump to the anchor (e.g. `#extraction-strategies`, `#content-processing`) rather than
   scanning linearly.
3. **Upstream documentation** — `https://docs.crawl4ai.com/` for current docs. Confirm the installed version with
   `python -c "import importlib.metadata; print(importlib.metadata.version('crawl4ai'))"` (or `crwl --version`) and
   check against the skill's [`VERSION`](../VERSION) file if surface names look wrong.
4. **Upstream source + issues** — `https://github.com/unclecode/crawl4ai`. Search `Issues` for the error message
   verbatim before re-deriving a fix. The codebase is small enough to grep when an API rename is suspected.
5. **`qmd query --collection stars`** — community blog posts, tutorials, and third-party examples mirrored in stars.
   Useful for non-obvious patterns (e.g. handling sites that detect headless Chrome via canvas fingerprinting).
6. **Ask the user** — only after the above. The question to ask is concrete: "I tried `wait_for=css:.foo` and the page
   timed out at 30s; the network panel suggests the selector is correct but content arrives via shadow DOM. Do you want
   me to try `wait_for=js:` instead, or do you know the actual rendering trigger?"

## Halt-vs-continue

**Continue (make a defensible choice, verify with a run):**

- Choosing between schema-based and LLM extraction when the page is borderline structured.
- Picking `wait_for` strategy (`networkidle` vs `domcontentloaded` vs selector) for an unfamiliar site — test, observe,
  refine.
- Selecting a content filter (`BM25` vs `PruningContentFilter`) — try one, look at `fit_markdown` length, swap if poor.

**Halt and ask:**

- The user mentioned credentials, a private API, or a paid SaaS source — confirm authorization scope before sending
  traffic.
- A `wait_for` or `js_code` snippet would interact with destructive UI (delete buttons, transfer flows). Even in QA,
  ask.
- The library raised an error message that explicitly names a config field you didn't set — likely a version bump
  renamed your surface. Verify the actual version (`importlib.metadata.version('crawl4ai')`) and the field name in the
  installed source before patching.
- The site's robots.txt or ToS would plausibly forbid scraping — ask the user about authorization before crawling.

## Worked examples

### Example 1 — `wait_for` selector never resolves

Symptom: `crwl https://app.example.com -c "wait_for=css:.results"` times out at 30s, but the page renders fine in a
browser.

What I did: queried `qmd query --collection solutions "playwright wait_for selector timeout shadow DOM"` (no hit), then
re-ran `crwl https://app.example.com -o html | rg -i "results" | head` to confirm the selector exists in raw HTML. It
did not — the content is rendered inside a shadow root the CSS selector can't pierce. Switched to
`wait_for="js:document.querySelector('app-root').shadowRoot.querySelector('.results') !== null"` per
`complete-sdk-reference.md#advanced-features`. Continue (verified by re-run, content extracted cleanly).

### Example 2 — `JsonCssExtractionStrategy` returns `[]` despite valid schema

Symptom: schema-driven extraction returns empty list even though `crwl ... -o markdown` clearly shows the target
elements.

What I did: queried `qmd query --collection solutions "JsonCssExtractionStrategy empty output baseSelector"`. Found a
solution doc that pointed at a common pitfall: `baseSelector` matching zero elements (e.g. `.product-card` when the site
uses `[data-product]`). Verified by `crwl ... -o html | rg "product-card\b"` → zero hits. Updated schema selector. The
schema-generation script `scripts/generate_schema.py` would have caught this on the first pass. Continue (verified by
re-run).

### Example 3 — `crwl` flag named in a third-party tutorial doesn't exist

Symptom: a blog post says `crwl --depth 3 https://example.com` for recursive crawling, but `crwl --help` shows no
`--depth` flag.

What I did: ran `crwl --version` to confirm installed version, then re-ran the query against the upstream README
(`https://github.com/unclecode/crawl4ai`) for the actual recursive-crawl entry point. Recursive crawling is an SDK-only
feature using `arun_many()` with a discovered URL list, not a `crwl` flag. The blog post was for an older fork. Halted
the CLI approach, switched to `scripts/batch_crawl.py` with a URL file. Halt → ask if the new approach was OK before
proceeding with credentials.
