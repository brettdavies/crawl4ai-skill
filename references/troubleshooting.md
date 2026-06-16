# Troubleshooting

Symptoms, likely causes, fixes. When a recipe in this list doesn't resolve the issue, follow
[Escalation](escalation.md).

## JavaScript content not loading

Symptom: `crwl <url> -o markdown` returns boilerplate or skeleton, but the page renders fine in a real browser.

Cause: page content arrives via JS after the initial HTML load. Crawl4AI returned the page before JS finished.

Fix: tell crawl4ai what to wait for.

```bash
crwl https://example.com -c "wait_for=css:.dynamic-content,page_timeout=60000"
```

If `wait_for=css:` selector doesn't exist in the raw HTML (shadow DOM, dynamic class names, etc.), use a JS predicate:

```bash
crwl https://example.com -c "wait_for=js:document.querySelector('.content') !== null,page_timeout=60000"
```

For infinite scroll, add `scan_full_page=true`:

```bash
crwl https://example.com -c "wait_for=css:.list-item,scan_full_page=true,page_timeout=60000"
```

## Bot detection / Cloudflare challenge

Symptom: `result.success` is `True` but `result.markdown` is the challenge page boilerplate, or you get a 403 / empty
response.

Cause: site detected automated traffic at one of four layers (headers, JS fingerprint, behaviour, IP).

Fix: layer the mitigations from [Anti-Detection](anti-detection.md) in order — random user agent first, then
`init_scripts` fingerprint patches, then undetected mode, then proxies. Verify each step actually rendered the real page
(not the challenge page) by inspecting `result.cleaned_html` directly.

```bash
crwl https://example.com -B templates/browser.yml -o all -v
```

## Content not extracted (`extracted_content` empty / `[]`)

Symptom: extraction returns empty even though the target elements are visible in `result.html`.

Causes (in order of likelihood):

1. `baseSelector` in the schema doesn't match any element. Verify:

   ```bash
   crwl <url> -o html | rg "<base-selector-text>"  # zero hits = wrong selector
   ```

2. Field `selector` is wrong (absolute when it should be relative to `baseSelector`, or vice versa).
3. Page hasn't finished rendering at extract time. Add `wait_for=css:<base-selector>`.

For LLM-based extraction returning malformed JSON, log `result.extracted_content` directly — the LLM may be wrapping
JSON in markdown fences or prose, which `json.loads()` then fails on.

## Session not persisting

Symptom: after `crwl https://site.com/login -C login_crawler.yml`, the second crawl with `session_id=user_session`
doesn't show the logged-in state.

Causes:

1. The login flow didn't actually complete. Add a strict `wait_for: "css:.dashboard"` (or whatever the post-login UI
   selector is). Check `result.cleaned_html` from the login crawl to confirm the session UI rendered.
2. `session_id` is misspelled or different between the two calls.
3. Server rejected the login. Inspect `result.cookies` and `result.status_code`.

Quick verify:

```bash
crwl https://site.com/protected -c "session_id=user_session" -o all -v | rg -i "session\|cookie"
```

## Crawl is slow

Symptom: single-URL crawls take 10s+; batch crawls feel slower than they should.

Causes (with fixes):

1. **Browser cold start** (~2s): unavoidable per process. Use `batch_crawl.py` to amortise across many URLs.
2. **Default cache mode**: `cache_mode: "bypass"` re-fetches every time. Use `"enabled"` during development, `"bypass"`
   only for production refresh runs.
3. **`scan_full_page: true` on a long page**: each scroll waits `scroll_delay` (default 0.3s); pages with 100+ scroll
   steps take 30s+. Disable when content is above the fold.
4. **`page_timeout` set too high**: a 60s timeout means failed crawls wait the full 60s. Tighten to 30s and let
   transient failures fail fast.
5. **`max_concurrent` too low for batch**: defaults to 5. With a stable network and target, 10-20 is often fine; watch
   memory.

## Schema generation produces nonsense

Symptom: `./scripts/generate_schema.py` returns a schema that extracts zero items, or wildly wrong fields.

Causes:

1. The instruction was too vague. "Extract products" is worse than "Extract product cards with name, price, and link;
   the cards are visually arranged in a grid."
2. The page renders content client-side and the LLM only saw the skeleton HTML. Try `wait_for=css:<the visible content>`
   in `generate_schema.py`'s `CrawlerRunConfig` and re-run.
3. The page has multiple repeating patterns (e.g. a "featured" carousel and a main grid). The LLM picked the wrong one.
   Inspect the schema, narrow the `baseSelector`, and retry.

## `crwl-doctor` says everything is fine, but crawls fail

Symptom: `crawl4ai-doctor` passes, but real crawls return network errors / empty responses.

Causes:

1. **DNS / network from your env**: `doctor` probes `crawl4ai.com`; your target may be behind a firewall, a VPN, or
   rate-limited.
2. **Proxy not picked up**: crawl4ai uses `proxy_config` (per-config), not `$HTTPS_PROXY`. If your network requires a
   proxy, set it in `templates/browser.yml`.
3. **TLS errors**: some intermediate CAs in corporate envs trip the browser. Try `ignore_https_errors: true` in
   `templates/browser.yml` for diagnosis only — don't ship with it on.

## Library upgrade broke my schema / config

Symptom: previously-working scripts fail after a crawl4ai version bump.

Fix: check the `VERSION` file at this skill's root — it records the version the skill was verified against. If you
upgraded crawl4ai past that, the field names or default values may have changed. Bump `VERSION` only after re-running
the bundled `tests/` against the new version.

If a regression appears between two versions, check the upstream `CHANGELOG.md`
(`https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md`) for the specific delta. The 0.7 → 0.8 transition in
particular changed several default behaviours (e.g. `AsyncLogger` now routes to stderr; `LLMExtractionStrategy` defaults
`extraction_type` to `"schema"`).
