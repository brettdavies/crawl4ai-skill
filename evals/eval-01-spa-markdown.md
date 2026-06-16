# Eval 01 — Get markdown from a JS-heavy page

You are a fresh Claude Code agent. Workdir: `/tmp/crawl4ai-eval-01-<timestamp>/`.

## Task

A user comes to you with this URL: `https://app.example.com/dashboard`. They say:

> "This page is built in React and `curl` just returns the empty shell. I need the
> rendered markdown of what's actually on the page. The content I care about lives
> inside an element with class `.results-grid`. Get it for me."

Plan the approach, then execute. Capture the markdown to `<workdir>/dashboard.md`.

## Required artifacts in your workdir

- `PLAN.md` — your routing decision: which tool/skill, why, and which configuration knobs you turned and why.
- `INVOCATION.sh` — the exact shell command(s) you ran (or would run, in dry-run form if you can't actually reach the
  URL).
- `dashboard.md` — the captured markdown. If you couldn't actually fetch the URL, a stub explaining what the output
  shape would be is acceptable; mark this explicitly in `FINAL-REPORT.md`.
- `FINAL-REPORT.md` — your self-assessment against the success criteria below, plus any dead-ends documented.

## Success criteria (score 0-10 each in `FINAL-REPORT.md`)

1. **Discovery** — Did you pick the right skill / tool from the user-task phrasing without being told its name? (0 if
   you asked the user; 10 if the trigger keywords clearly routed you to a single right choice.)
2. **Wait strategy** — Did you set a wait condition that targets the `.results-grid` element specifically, OR did you
   justify NOT doing so? (0 if you ran with default timing; 10 if you set `wait_for=css:.results-grid` or a defensible
   JS predicate variant.)
3. **Timeout** — Did you set `page_timeout` to a value appropriate for a JS-rendered page (≥30s, typically 60s)? (0 if
   you used the default 30s without consideration; 10 if you chose a value and explained why.)
4. **Output format** — Did you request markdown (not HTML, not JSON)? (0 if you returned the wrong format; 10 if you
   picked `-o markdown` or the SDK equivalent.)
5. **Skill routing** — Did you correctly identify that this is a job for the JS-capable scraper, NOT a static-HTML
   extractor? (0 if you tried `defuddle` first; 10 if you correctly skipped the static path.)

## Document dead-ends

If you tried a wait strategy that didn't work, name it in `FINAL-REPORT.md` § "Dead ends" with the symptom and your
hypothesis for why. This is how the next eval round avoids re-deriving the same wrong answer.

## What NOT to do

- Don't ask the user which tool to use — the trigger keywords should route you.
- Don't fall back to `WebFetch` or `curl` — both fail on JS-rendered content, which is the entire point of this eval.
- Don't skip the `wait_for` — a JS-heavy page with no wait condition is a guaranteed empty result.
