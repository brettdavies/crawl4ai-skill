# Evals

Each `eval-*.md` is a self-contained prompt for a fresh agent: no project context, no skill name, no underlying tool
name. The agent must discover the right tool from the user-task phrasing alone — that's the discovery test.

Workdirs land in `/tmp/crawl4ai-eval-<id>/`, never committed.

| Eval                                                           | Tests                                                  |
| -------------------------------------------------------------- | ------------------------------------------------------ |
| [eval-01-spa-markdown.md](eval-01-spa-markdown.md)             | Discovery + wait_for strategy for JS-rendered pages    |
| [eval-02-extract-products.md](eval-02-extract-products.md)     | Schema generation pipeline + CSS extraction routing    |
| [eval-03-topic-domain-crawl.md](eval-03-topic-domain-crawl.md) | URL discovery → filtering → batch crawl composition    |
| [eval-04-render-cached-html.md](eval-04-render-cached-html.md) | `raw:` URL rendering for screenshot from existing HTML |

## Running an eval

Dispatch the prompt to a fresh agent (e.g. via Claude Code in a new session, or the `Agent` tool with `isolation:
"worktree"`). The eval should:

1. Discover the relevant skill from its frontmatter description.
2. Read the skill's references as needed (escalation, recipes, the topic-specific reference).
3. Produce the required artifacts in its workdir.
4. Self-score against the success criteria.
5. Document any dead-ends in `FINAL-REPORT.md`.

A passing eval scores ≥7/10 on each numbered criterion AND surfaces no silent-failure modes the prompt names. Any score
below 7 OR any regression vs the previous eval round is a blocking finding.

## When to re-run

- After bumping `VERSION` and the PEP 723 pins (catches regressions from the upstream library upgrade).
- After substantive SKILL.md or references edits (catches discoverability or routing regressions).
- Before declaring a major refactor done.
