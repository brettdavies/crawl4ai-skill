# Eval 02 — Extract structured products from an e-commerce site

You are a fresh Claude Code agent. Workdir: `/tmp/crawl4ai-eval-02-<timestamp>/`.

## Task

A user comes to you with this URL: `https://shop.example.com/category/widgets`. They say:

> "I need to pull all the products on this page into a JSON list. Each product
> should have `name`, `price`, and a `link` to the detail page. This is a one-off
> right now, but I want to repeat it across maybe a dozen URLs later this week
> without paying per-page LLM costs."

Plan the approach, then execute.

## Required artifacts in your workdir

- `PLAN.md` — your routing decision. Specifically: did you choose (a) LLM extraction per-URL, (b) a CSS schema generated
  once and reused, or (c) a hand-written schema? Justify with the user's stated constraint ("dozen URLs", "without
  paying per-page LLM costs").
- `INVOCATION.sh` — exact commands.
- `shop_schema.json` — the schema you derived (LLM-generated or hand-written).
- `products.json` — the extracted result. If you can't reach the URL, a stub with the expected shape is acceptable; mark
  this in `FINAL-REPORT.md`.
- `FINAL-REPORT.md` — self-assessment.

## Regression-test prior fixes

This eval runs after eval-01. Verify that the eval-01 fixes are still in place:

- **Wait strategy is documented somewhere** — the recipes / troubleshooting references should still cover JS-rendered
  pages. (`worked` / `regressed` / `not-touched`.)

Classify in `FINAL-REPORT.md` § 4. Any `regressed` finding is blocking.

## Success criteria (score 0-10 each)

1. **Pipeline choice** — Did you choose the schema-generation + schema-reuse pipeline (option b), based on the user's
   stated "repeat across a dozen URLs without per-page LLM costs"? (0 if you chose option a; 10 if option b with
   reasoning.)
2. **Schema derivation** — Did you use the dedicated schema-generation script (one LLM call), OR did you hand-write the
   schema? Either is acceptable IF you noted the trade-off; 0 if you re-used LLM extraction for every URL instead.
3. **Schema validation** — Did you sanity-check the derived schema against ONE URL before declaring it done? A schema
   that returns `[]` on the first real page is a silent failure mode. (0 if you skipped validation; 10 if you ran a
   single-URL extract first and inspected the result.)
4. **Batch-ready** — Did your invocation handle the "dozen URLs later this week" use case (i.e. did you point at a
   script / config that takes a URL list as input)? (0 if your output only handles one URL; 10 if the next call is
   `<batch-tool> urls.txt schema.json`.)
5. **Schema field names** — Do the field names in your schema match what the user asked for (`name`, `price`, `link`)?
   (0 if you renamed; 10 if exact match.)

## Document dead-ends

If the schema-generation step produced a schema with the wrong `baseSelector`, name the symptom in `FINAL-REPORT.md` §
"Dead ends" and your fix.

## What NOT to do

- Don't pay an LLM call per URL when the user explicitly said "without paying per-page LLM costs."
- Don't hand-write a schema before checking whether the bundled schema-generation script exists.
- Don't return JSON without validating the schema produces non-empty output on a real page first.
