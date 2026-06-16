# Contributing

Contributions are welcome under the dual Apache-2.0 OR MIT license that the rest of the repo carries (SPDX `MIT OR
Apache-2.0`). Opening a pull request signals you agree to license your contribution under those same terms.

Project-level conventions for agents and humans working inside the repo live in [AGENTS.md](AGENTS.md); the consumer-
facing surface (install paths, bundle layout, scripts) lives in [README.md](README.md); the skill itself lives in
[SKILL.md](SKILL.md). Read whichever is relevant before you start.

## Filing issues

Open an issue at <https://github.com/brettdavies/crawl4ai-skill/issues>. Include reproducer steps, the agent host you
ran the skill in (Claude Code, Codex, Cursor, OpenCode, Cline, or other), and the Crawl4AI library version on your
system (`pip show crawl4ai` or check the value pinned in [`VERSION`](VERSION)).

## Proposing changes

1. Cut a branch from `main` named `feat/<topic>` or `fix/<topic>`.
2. Make the change. Run the tests under `tests/` and confirm they still pass.
3. Open a PR against `main`. The repo standard PR template loads automatically; fill it in.

## Conventions

- **Commit subjects**: Conventional Commits (`type(scope): description`). Use `feat:` or `fix:` for anything
  user-observable (default behavior, script names, reference content, bundle layout). `chore:`, `style:`, `test:`,
  `ci:`, `build:` are excluded from the changelog.
- **Prose**: keep README and `SKILL.md` tight. Avoid em-dash density above 3 per 1000 words, "It's not X, it's Y"
  constructions, and filler openers.
- **Markdown**: passes `markdownlint-cli2` against the repo's `.markdownlint-cli2.yaml`.
- **Library pin**: if your change requires a different Crawl4AI library version, update [`VERSION`](VERSION) and verify
  every reference doc, every script, and every eval against the new release before opening the PR.

## Scope

This bundle wraps Crawl4AI for agent hosts. Upstream library bugs belong at the
[Crawl4AI repo](https://github.com/unclecode/crawl4ai), not here. Open issues here for: bundle layout, SKILL.md routing,
reference doc accuracy, helper script behavior, fixture / eval coverage, or skill-format compatibility with a specific
agent host.
