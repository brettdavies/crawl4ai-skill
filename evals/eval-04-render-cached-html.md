# Eval 04 — Render a screenshot from HTML I already have

You are a fresh Claude Code agent. Workdir: `/tmp/crawl4ai-eval-04-<timestamp>/`.

## Task

A user says:

> "I already pulled this page's HTML into a variable — it's about 80KB. I just
> need a screenshot of how it would render. I don't want to make another network
> fetch. The page uses relative image URLs against
> `https://example.com/` for resolution. And I need the **full page**, not just
> what fits in the default viewport — it's a long article."

The HTML string is supplied as an environment variable `HTML_CONTENT` (~80KB). For this eval, assume it represents a
real rendered page.

Plan the approach, then execute.

## Required artifacts in your workdir

- `PLAN.md` — the routing decision. Specifically, explain why you do or do not do a network fetch.
- `INVOCATION.py` (or `INVOCATION.sh`) — the exact code/command. Inline the HTML loading from `HTML_CONTENT` rather than
  fetching from network.
- `screenshot.png` — the captured render. Stub acceptable if the workdir can't actually run crawl4ai; mark in
  `FINAL-REPORT.md`.
- `FINAL-REPORT.md` — self-assessment.

## Regression-test prior fixes

After evals 01-03. Verify each by file + section + expected substance:

- **Schema pipeline** (eval-02). `references/recipes.md` § 3 still names the `generate_schema.py` →
  `extract_with_schema.py` → `batch_extract.py` flow. Classify `worked` / `regressed` / `not-touched`.
- **URL discovery** (eval-03). `references/url-discovery.md` still surfaces `AsyncUrlSeeder` + `SeedingConfig` with the
  `query` + `score_threshold` fields. Classify same.
- **JS-rendered page handling** (eval-01). `references/troubleshooting.md` § "JavaScript content not loading" still
  documents `wait_for=css:<selector>` and the JS-predicate fallback. Classify same.

Any `regressed` is blocking.

## Success criteria (score 0-10 each)

1. **No-network choice** — Did you choose a code path that does NOT fetch `https://example.com/` again? (0 if you
   fetched; 10 if you used the `raw:` or `file://` URL form.)
2. **`raw:` vs `file://`** — Did you pick `raw:` (HTML in hand as a string) over `file://` (you'd have to write the HTML
   to disk first)? (0 for unnecessary disk I/O; 10 for `raw:` direct.)
3. **`base_url` set** — Did you set `base_url="https://example.com/"` so the relative image URLs in the HTML resolve
   correctly? (0 if you forgot; 10 if set and explained.)
4. **Screenshot requested** — Did you configure the crawler to actually emit the screenshot (e.g. `screenshot=True`)? (0
   if you got markdown / HTML back without a screenshot; 10 if `result.screenshot` is the payload.)
5. **Skill routing** — Did you correctly identify this as a job for the browser-render tool (not a static-HTML
   extractor; not a markdown converter)? (0 if you tried `defuddle` or `markdown-convert`; 10 if you correctly routed to
   the browser-render path.)
6. **Full-page screenshot escalation** — Did you escalate to find the full-page-screenshot field name rather than guess
   it? (0 if you guessed and were wrong, 5 if you guessed and happened to be right, 10 if you verified the field name
   via the complete reference, upstream docs, or library introspection before using it.)
7. **Full-page dimensional proof** — Report the rendered PNG's `(width, height)` to `FINAL-REPORT.md` § "Dimensions"
   (one-line PIL or `identify` invocation is fine). A viewport-only screenshot is height = `viewport_height` (default
   1080); a full-page screenshot is materially taller. Score 0 if `screenshot.png` is missing or you reported only "the
   call succeeded" without dimensions; 5 if the call succeeded but height ≤ viewport_height (you got the viewport, not
   the full page); 10 if height >> viewport_height AND you reported the numbers.

## Forced escalation

The user's "full page, not just the viewport" requirement is **not covered** by the skill's references — recipes.md
shows `screenshot=True` but does not surface the full-page vs viewport-only field name. You are required to escalate to
find it: check `complete-sdk-reference.md` for `CrawlerRunConfig` screenshot-related fields, fall back to upstream docs,
and finally introspect the installed library if neither resolves it (`python -c "from crawl4ai import CrawlerRunConfig;
help(CrawlerRunConfig.__init__)" | grep -i screenshot`).

Document in `FINAL-REPORT.md` § "Escalation" the lookup path you took and the actual field name you used. Per the
escalation iron rule: **do not guess** a field name like `full_page=True` or `screenshot_full_page=True` from training
data without verification. Failing to escalate (and guessing) caps the score at 5 even if the guess happens to be right.

## What NOT to do

- Don't fetch the URL again. The user explicitly said they have the HTML and don't want another fetch.
- Don't write the HTML to a temp file just to pass `file://` — `raw:` exists exactly to skip that step.
- Don't ignore `base_url`. Relative image URLs render as broken images without it; the screenshot will look wrong even
  if the call "succeeds."
