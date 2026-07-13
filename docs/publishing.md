# Publishing Acyro

The repository publishes tested distributions from GitHub Releases using PyPI
Trusted Publishing. No PyPI API token is required.

## Trusted Publishing

The PyPI project uses this trusted publisher configuration:

- PyPI project name: `acyro`
- GitHub owner: `xjn2005`
- Repository name: `Acyro`
- Workflow filename: `publish.yml`
- Environment name: `pypi`

The matching GitHub environment is configured under **Settings →
Environments**.

## Release

1. Update `version` in `pyproject.toml`.
2. Run `uv lock`, `uv run pytest -q`, `uv run ruff check .`, and `uv build`.
3. Commit and push the release changes.
4. Create a tag matching the version, such as `v0.1.1`.
5. Publish a GitHub Release from that tag.

Publishing the GitHub Release triggers `.github/workflows/publish.yml`. The
workflow tests and builds the project, then exchanges GitHub's OIDC identity
for a short-lived PyPI credential and uploads `dist/`.

PyPI release files cannot be replaced. If publishing fails after PyPI accepts a
file, increment the version before trying again.
