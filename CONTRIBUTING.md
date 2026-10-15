# Development and releases

Create focused branches from `dev` with names such as `codex/credit-clarity-banking-progression`. Open pull requests against `dev` and name them after the resulting behavior, for example **Clarify Credit controls and connect banking research**. Group related work in reviewable commits whose subjects explain the change. Avoid version numbers in branch names, commit subjects and PR titles. Do not rewrite merged history to rename older work.

Each PR should explain the problem, the resulting behavior and the validation performed. Keep engine evidence distinct from offline checks, and record outstanding visual or gameplay checks. Generated runtime files must accompany their generator changes. Test with a disposable Florence campaign and separately installed CMF.

Versioned distributions are produced by GitHub Releases. After the intended changes have been reviewed and integrated, create a release from the chosen commit with a semantic tag such as `v0.1.0` or `v0.1.0-rc.1`. The release workflow validates the committed runtime and attaches a ZIP plus its SHA-256 manifest. It stamps the release tag into the staged mod metadata without changing the source checkout or creating a version-bump PR. Mark prereleases in GitHub when appropriate.

The version in `design/tuning.json` is the development metadata baseline, not a PR name or release promise. Feature work does not increment it. A release's tag, packaged metadata and assets identify its distributed version. Keep game compatibility and CMF dependency versions separate from the mod release number.

To inspect a release package locally before publishing:

```powershell
./tools/stage_release.ps1 -ReleaseVersion v0.1.0-rc.1
```

This stages files only. It does not create a tag, publish a GitHub Release or upload to the Workshop.
