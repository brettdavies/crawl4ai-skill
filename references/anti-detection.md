# Anti-Detection

When a site rejects the crawl with a Cloudflare interstitial, a `403`, an empty response, or a "human verification"
page, the question is which layer is detecting you. Four layers, in increasing order of expense.

| Layer                  | Mechanism                                                              | Mitigation                                                                   |
| ---------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Header / fingerprint   | Server checks `User-Agent`, header order, missing browser headers      | Browser strategy with `user_agent_mode: "random"`                            |
| JavaScript fingerprint | Page-side JS checks `navigator.webdriver`, canvas, WebGL, font metrics | `BrowserConfig.init_scripts` to patch detection surfaces before site JS runs |
| Behavioural            | Click rate, scroll patterns, mouse-move absence                        | Undetected mode (Patchright) with random pacing                              |
| IP reputation          | Rate limits or blocklists on hosting / datacentre IPs                  | `proxy_config` routed through a residential proxy                            |

Apply mitigation in this order — each layer up adds cost and complexity.

## Layer 1 — Header / fingerprint

The browser strategy already sets realistic headers. For sites that block known datacentre `User-Agent` strings, rotate
with `user_agent_mode: "random"`:

```yaml
# templates/browser.yml
headless: true
user_agent_mode: "random"
viewport_width: 1920
viewport_height: 1080
```

```bash
crwl https://example.com -B templates/browser.yml
```

## Layer 2 — JavaScript fingerprint

`BrowserConfig.init_scripts` runs **before** any site JavaScript. This is the right place for patches like masking
`navigator.webdriver`. Compare to `CrawlerRunConfig.js_code`, which runs **after** the page loads — too late for
fingerprint detection that fires at load time.

```python
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    headless=True,
    init_scripts=[
        # Mask the webdriver flag
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
        # Spoof common automation indicators
        "window.chrome = window.chrome || {runtime: {}}",
        "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})",
    ],
)
```

The CLI accepts the same field in YAML form:

```yaml
# templates/browser.yml (uncomment the init_scripts: section)
init_scripts:
  - "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

## Layer 3 — Undetected mode (Patchright)

When fingerprint patches are not enough, Patchright (an undetected Chromium fork) handles a broader set of evasions.

The bundled `crawl4ai-setup` warns about Patchright install when it can't run `apt-get` (needs sudo for OS-level
dependencies). If undetected mode is required, install with:

```bash
sudo "$(uv tool dir)/crawl4ai/bin/python3" -m patchright install --with-deps
```

Skip if you don't need it — Patchright is a separate ~150MB Chromium binary; the default Playwright Chromium handles
most cases when paired with `init_scripts`.

## Layer 4 — Proxies

`proxy_config` routes traffic through an upstream proxy. Works with **both** the browser strategy AND the non-browser
`HTTPCrawlerStrategy` (the latter is the cheap path for static fetches behind a corporate proxy).

```python
browser_config = BrowserConfig(
    headless=True,
    proxy_config={
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "pass",
    },
)
```

YAML form:

```yaml
# templates/browser.yml
proxy_config:
  server: "http://proxy.example.com:8080"
  username: "user"
  password: "pass"
```

For rotating residential proxies, configure your provider's endpoint; the library does not bundle a rotation manager.

## CDP attachment (use the browser that already exists)

If a long-lived Chromium daemon is already running (gstack's `/browse` uses one; a manually-launched Chrome with
`--remote-debugging-port` also works), connect crawl4ai to it via CDP instead of spawning a new browser. Use when:

- Iterating on a scrape and the cold-start cost matters
- The crawl needs to inherit existing session state (cookies, logged-in tabs)
- You want one fewer Chromium binary on disk

```python
browser_config = BrowserConfig(
    headless=True,
    use_managed_browser=True,
    # cdp_url passed via the underlying Playwright connection; verify the
    # exact field name against the installed library before relying on it
)
```

The exact `cdp_url` / `ws_endpoint` field name evolved across 0.8.x; before relying on it for a production flow, check
the field name in the installed library:

```bash
python -c "from crawl4ai import BrowserConfig; help(BrowserConfig.__init__)" | head -50
```

## Verification

After applying any mitigation, verify the crawl actually rendered the protected content rather than the interstitial:

```bash
crwl https://example.com -B templates/browser.yml -o all -v
# Check `result.cleaned_html` for the real page content vs a challenge page
```

A successful crawl that returned the Cloudflare verification page is a silent failure — `result.success` is `True` but
the markdown is challenge-page boilerplate.
