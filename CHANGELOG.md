# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-16

Major release. Verified against the Crawl4AI library at version 0.8.9 (recorded in `VERSION`). The repo is now the skill
bundle: `SKILL.md` and the skill directories live at the repo root and load directly with `git clone <repo>
~/.claude/skills/crawl4ai`.

### Added

- `VERSION` file pinning the crawl4ai library version the skill is verified against.
- `templates/` directory carrying browser, crawler, content-filter, and extraction YAML configs the scripts and SKILL.md
  reference (`browser.yml`, `crawler.yml`, `extract_css.yml`, `extract_llm.yml`, `filter_bm25.yml`,
  `filter_pruning.yml`, `login_crawler.yml`, `css_schema.json`).
- `evals/` directory carrying four eval scenarios for verifying skill behavior, with a README.
- `fixtures/` directory carrying the schema-generation reference fixture (sample product HTML, expected schema, expected
  JSON output), with a README.
- Reference guides under `references/`: `anti-detection.md`, `content-filters.md`, `escalation.md`, `recipes.md`,
  `troubleshooting.md`, `url-discovery.md`.
- Focused scripts under `scripts/`: `batch_crawl.py`, `batch_extract.py`, `generate_schema.py`,
  `extract_with_schema.py`, `extract_with_llm.py`.
- Test coverage for fixtures under `tests/test_fixtures.py`.
- `LICENSE-APACHE` and `LICENSE-MIT` carrying the full license texts; `LICENSE` summarizes the dual-license model (SPDX
  `MIT OR Apache-2.0`).

### Changed

- **Layout:** the skill bundle lives at the repo root. The previous `crawl4ai/` wrapper directory is gone. `SKILL.md`
  and its companion directories are direct children of the repo root.
- **Default JS-render wait** switches from `wait_for=css:body` to `wait_until=networkidle` across `SKILL.md` and every
  bundled script. `wait_for=css:body` was satisfied at t=0 on every HTML response and added no real wait;
  `wait_until=networkidle` waits for ~500ms of network quiet post-load.
- **License:** dual Apache-2.0 OR MIT (was MIT-only). Existing MIT consumers retain MIT terms.
- **CLI guide drift fixes:** the deprecated `anthropic/claude-3-sonnet` LLM provider reference is replaced with a
  pointer to the LiteLLM provider list, the LLM-extraction example no longer passes a stray `-s llm_schema.json` (the
  schema lives inside `extract_llm.yml`), and the `filter_pruning.yml` snippet drops the `query` key (pruning filters do
  not take one) and adds the required `threshold_type: fixed`.
- `SKILL.md`, the existing reference guides, the scripts, the tests, and the evals all refresh against Crawl4AI 0.8.9.
- `README.md` install section: single `git clone` into `~/.claude/skills/crawl4ai` for Claude Code; staging-dir zip
  snippet for Claude Desktop that includes `templates/`, `evals/`, `fixtures/`, and `VERSION`. Helper-scripts list and
  E-commerce Product Monitoring example now match the new script names. License section reflects the dual-license model.
- `.gitignore` extended with the script-output patterns (`output.md`, `screenshot.png`, `batch_results.json`,
  `batch_extracted.json`, `batch_markdown/`, `generated_schema.json`, `extracted_data.json`, `manual_extracted.json`,
  `llm_extracted.json`) so script invocations from the repo root no longer pollute the working tree.

### Removed

- `marketplace/metadata.json`. No Claude consumer reads it; the data it carried lives on SKILL.md frontmatter, GitHub
  topics, README, and LICENSE.
- The prebuilt `crawl4ai.zip` artifact. README documents how to build the zip from the tree on demand.
- The monolithic `scripts/extraction_pipeline.py`. Its responsibilities split across `scripts/generate_schema.py` and
  `scripts/extract_with_schema.py`.
- `scripts/batch_crawler.py`. Replaced by `scripts/batch_crawl.py`.

### Breaking Changes

- Symlinks pointing into the previous `crawl4ai-skill/crawl4ai/` no longer resolve; repoint at the repo root.
- Script callers referencing `scripts/extraction_pipeline.py` switch to `scripts/generate_schema.py` plus
  `scripts/extract_with_schema.py`. Callers of `scripts/batch_crawler.py` switch to `scripts/batch_crawl.py`.
- License changes from MIT-only to dual Apache-2.0 OR MIT.

## [1.0.0] - 2025-12-02

### Added

- Initial release of Crawl4AI Claude Skill
- Complete skill documentation in `SKILL.md`
- CLI guide with comprehensive command-line interface reference
- SDK guide with Python SDK quick reference
- Complete SDK reference documentation (5900+ lines)
- Helper scripts:
- `basic_crawler.py` - Simple markdown extraction
- `batch_crawler.py` - Multi-URL processing with concurrency
- `extraction_pipeline.py` - Schema generation and extraction pipeline
- Test suite with comprehensive coverage:
- Basic crawling tests
- Markdown generation tests
- Data extraction tests
- Advanced patterns tests (sessions, proxies, batch crawling)

### Features

- Web crawling with full JavaScript support
- Schema-based CSS extraction (LLM-free, 10-100x more efficient)
- LLM-based extraction for complex content
- Markdown generation with content filtering
- Session management for authenticated crawling
- Batch/concurrent URL processing
- Both CLI and Python SDK interfaces
- Comprehensive documentation and examples

### Documentation

- Complete skill instructions in `SKILL.md`
- CLI reference guide
- SDK reference guide
- Full API documentation
- Usage examples for common scenarios
- Troubleshooting guide
