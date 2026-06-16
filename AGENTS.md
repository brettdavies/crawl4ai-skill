---
name: crawl4ai
description: Portable agent skill for JS-aware crawling and schema-based extraction (wraps the Crawl4AI CLI and Python SDK).
repository: https://github.com/brettdavies/crawl4ai-skill
license: MIT OR Apache-2.0
verified-against: Crawl4AI 0.8.9
---

# AGENTS.md

This repo is a portable agent skill in the Anthropic SKILL.md format. The bundle layout, install paths, and
consumer-facing contract live in [README.md](README.md). The skill itself, with all triggers, defaults, and routing,
lives in [SKILL.md](SKILL.md). The contributor flow (issues, branches, PR conventions) lives in
[CONTRIBUTING.md](CONTRIBUTING.md). Read those before making changes.

## Bundle conventions

- The skill is verified against the Crawl4AI library version pinned in [`VERSION`](VERSION). Bumping that version
  requires verifying every reference doc, every script, and every eval still works against the new release.
- Defaults are settled. The current JS-render wait is `wait_until=networkidle`. Do not regress to `wait_for=css:body`;
  the `<body>` element exists at t=0 on every HTML response, so it adds no real wait.
- Bundled scripts use PEP 723 inline metadata so consumers can run them via `uv run`. Keep the dependency floor in step
  with `VERSION`.
- The schema-generation fixture under `fixtures/` is the contract for `scripts/generate_schema.py`. If you change the
  schema format, update the fixture and the corresponding test in `tests/test_fixtures.py`.

## Repo conventions

- Branch discipline: `main` is protected. Code changes go through a `feat/...` or `fix/...` branch and a PR. Doc-only
  edits (README, AGENTS, CHANGELOG) may land directly on `main`.
- Conventional Commits in commit subjects. Use `feat:` or `fix:` for anything user-observable (default behavior, script
  names, reference content, bundle layout). `chore:`, `style:`, `test:`, `ci:`, `build:` are excluded from the changelog
  by the parser this repo targets.
- License: dual Apache-2.0 OR MIT (SPDX `MIT OR Apache-2.0`). Contributions are accepted under this license.

## Testing

```bash
cd tests
python run_all_tests.py
```

The suite covers basic crawling, markdown generation, extraction, advanced patterns, and the schema-generation fixture.

## Quality bar

- Markdown is linted via `markdownlint-cli2` against `.markdownlint-cli2.yaml`.
- Reference docs are the contract for the skill's behavior. Touch `complete-sdk-reference.md` surgically; it tracks the
  upstream library API.

## When NOT to edit

- Do not edit `LICENSE`, `LICENSE-APACHE`, or `LICENSE-MIT` independently of a deliberate relicense.
- Do not bump `VERSION` without verifying the bundle still works against the new library version.
- Do not add `wait_for=css:body` to any new script or example.
