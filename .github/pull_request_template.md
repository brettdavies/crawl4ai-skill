## Summary

<!-- Provide a brief overview of the changes in this PR. What feature/fix/improvement does this introduce?

     SCOPE: Describe the net diff only — what the merged result looks
     like compared to the base branch. NOT commit history, intermediate
     state, or how the cherry-picks were assembled.

     EXCLUDE all verification artifacts:
- Triple-diff output / stats (A, B, C blocks)
- Leak-check output ("no guarded paths leaked", "guard-main-docs runs clean")
- Patch-id cherry-check counts
- Pre-push gate results, CI status, prose-scrub findings
- Any "I ran X and it returned Y" narration

     Anomalies get fixed before push, not audit-trailed in the body.
-->

## Changelog

<!-- CRITICAL: This section is the source of truth for CHANGELOG.md.
     generate-changelog.py extracts these categorized bullets verbatim
     into the release changelog. Write carefully — this IS the changelog.

     AUDIENCE: Users and operators. Write from their perspective.

     INCLUDE: new features, changed behavior, breaking changes, fixed bugs,
     new/removed config, new dependencies users need to know about.

     EXCLUDE: internal refactors, test additions, code cleanup, CI changes,
     regenerated files, implementation details (unreachable!() arms, import
     reordering, cargo_bin migration, cfg gates, etc.). Document those in
     the PR body text or Files Modified section — NOT here.

     RULES:
- 1-5 bullets per PR. Fewer is better. One-line fixes get one bullet.
- Delete empty ### sections entirely — don't leave blank categories.
- Each bullet starts with a verb: Add, Fix, Change, Remove, Deprecate.
- Don't duplicate the PR title — expand on it or provide context.
- If the PR has NO user-facing changes (pure refactor, test-only, CI), leave this section empty or omit it. The PR still
  appears in git history; it just won't clutter the changelog. -->

### Added

-

### Changed

-

### Fixed

-

### Documentation

-

## Type of Change

<!-- Check the type that applies to this PR -->

- [ ] `feat`: New feature (non-breaking change which adds functionality)
- [ ] `fix`: Bug fix (non-breaking change which fixes an issue)
- [ ] `refactor`: Code refactoring (no functional changes)
- [ ] `perf`: Performance improvement
- [ ] `docs`: Documentation update
- [ ] `test`: Adding or updating tests
- [ ] `chore`: Maintenance tasks (dependencies, config, etc.)
- [ ] `ci`: CI/CD configuration changes
- [ ] `style`: Code style/formatting changes
- [ ] `build`: Build system changes
- [ ] `BREAKING CHANGE`: Breaking API change (requires major version bump)

## Related Issues/Stories

<!-- Link to related issues, stories, or documentation -->

- Story:
- Issue:
- Architecture:
- Related PRs:

## Testing

<!-- Describe the testing approach and results -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

**Test Summary:**

- Unit tests: X passing
- Integration tests: Y passing
- Coverage: Z%

## Files Modified

<!-- List the main files modified in this PR -->

**Modified:**

**Created:**

**Renamed:**

**Deleted:**

## Key Features

<!-- Optional: Highlight key features or capabilities introduced -->

-

## Benefits

<!-- Optional: Describe the benefits (performance, security, compliance, UX, etc.) -->

-

## Breaking Changes

<!-- If this PR contains breaking changes, describe them and the migration path -->

- [ ] No breaking changes
- [ ] Breaking changes described below:

## Deployment Notes

<!-- Any special deployment considerations, migrations, or configuration changes needed -->

- [ ] No special deployment steps required
- [ ] Deployment steps documented below:

## Screenshots/Recordings

<!-- Optional: Add screenshots or recordings for UI changes -->

## Checklist

- [ ] Code follows project conventions and style guidelines
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Self-review of code completed
- [ ] Tests added/updated and passing
- [ ] No new warnings or errors introduced
- [ ] Changes are backward compatible (or breaking changes documented)

## Additional Context

<!-- Optional: Add any additional context, screenshots, or information -->

---

<!--
PR Title Format: <type>(<scope>): <description>

Examples:
- feat(auth): add OAuth2 authentication provider
- fix(api): resolve rate limiting edge case
- docs(readme): update installation instructions
- refactor(db): optimize query performance
- chore(deps): upgrade to bun 1.3.1
-->
