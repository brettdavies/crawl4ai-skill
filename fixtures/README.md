# Fixtures

Deterministic before/after pair for `scripts/extract_with_schema.py`. The runner lives at `tests/test_fixtures.py` and
ships in the standard test suite — invoke directly or via `tests/run_all_tests.py`.

```bash
./tests/test_fixtures.py                  # exit 0 on match, 1 on diff
./tests/run_all_tests.py                  # runs this fixture pair plus the others
```

Pass means the wrapper script + the installed library still produce the documented output shape against fixed HTML. A
diff means either the upstream library's scraping fidelity drifted (regression), the schema is wrong, or the fixture
HTML changed shape. Bump `VERSION` only after this passes against the new library version.

| File                            | Role                                           |
| ------------------------------- | ---------------------------------------------- |
| `sample-products.html`          | Fixed HTML input. Three `.product-card` items. |
| `sample-products-schema.json`   | The `JsonCssExtractionStrategy` schema.        |
| `sample-products-expected.json` | Expected extracted output.                     |
