# Eval 03 — Topic-bound crawl of a whole domain

You are a fresh Claude Code agent. Workdir: `/tmp/crawl4ai-eval-03-<timestamp>/`.

## Task

A user says:

> "Get me clean markdown from every blog post on `example.com` that's about
> machine learning. I don't have the URL list — start from the domain. I care
> about relevance, not coverage; skip pages that mention ML once in passing."

Plan the approach, then execute.

## Required artifacts in your workdir

- `PLAN.md` — describe the two distinct phases (URL discovery, then content crawl), and which tool/approach you picked
  for each.
- `INVOCATION.sh` — exact commands (or dry-run equivalents).
- `urls.txt` — the discovered, filtered URL list.
- `ml_markdown/` — directory of `.md` files, one per URL. Stub acceptable if you can't reach the network.
- `FINAL-REPORT.md` — self-assessment.

## Regression-test prior fixes

After eval-01 and eval-02. Verify:

- **Schema-generation pipeline is still documented** (eval-02). Classify `worked` / `regressed` / `not-touched`.
- **JS-rendered page handling is still documented** (eval-01). Classify same.

Any `regressed` is blocking.

## Success criteria (score 0-10 each)

1. **Two-phase architecture** — Did you split URL discovery from page crawl, rather than trying to do both in one pass?
   (0 if you tried to combine; 10 if discovery → urls.txt → batch crawl was your shape.)
2. **Discovery tool choice** — Did you pick the relevance-scored URL discovery surface (not the maximum-coverage one),
   based on the user's stated preference for relevance over coverage? (0 if you picked the coverage tool and tried to
   filter post-hoc; 10 if you picked the BM25-scored seeder with `query` + `score_threshold`.)
3. **Pattern filter** — Did you also constrain the URL discovery by URL path pattern (e.g. `*/blog/*`) to skip non-blog
   pages? (0 if no path filter; 10 if you added a sensible glob.)
4. **Score threshold** — Did you set a `score_threshold` to drop URLs that mention ML only in passing? (0 if you took
   everything; 10 if you set a non-trivial threshold and explained the reasoning.)
5. **Batch composition** — Did the discovery output flow naturally into the batch crawl (i.e. `urls.txt` is the input to
   the next step, not a manual copy-paste)? (0 if you reformatted between steps; 10 if the handoff is clean.)

## Dry-run gate

If you can't actually reach the network, do a `--dry-run` equivalent: print the commands that would execute, with the
resolved arguments. Save to `dryrun-output.txt`. The score caps at 5 if `dryrun-output.txt` is missing for
network-blocked runs.

## What NOT to do

- Don't try to manually enumerate blog URLs by guessing patterns. The skill has URL-discovery surfaces for exactly this
  case.
- Don't run an LLM call against every page just to check "is this about ML?" — the discovery layer's BM25 scoring solves
  this cheaper.
- Don't skip the path pattern. Without `pattern="*/blog/*"`, you'll get the about page, the contact page, and every
  other URL in the sitemap.
