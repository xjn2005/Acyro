# Publishing Acyro

The repository is prepared to publish a tested package from a GitHub Release
using PyPI Trusted Publishing. No PyPI API token is required.

## One-time setup

1. Create a GitHub repository named `acyro` and push this project to it.
2. In the GitHub repository, open **Settings → Environments**, create an
   environment named `pypi`, and optionally require reviewer approval.
3. Sign in to PyPI, open **Account settings → Publishing**, and add a pending
   GitHub publisher with:

   - PyPI project name: `acyro`
   - GitHub owner: your GitHub username or organization
   - Repository name: `acyro`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`

The pending publisher creates the PyPI project on its first successful upload.
It does not reserve the name before that upload.

## Release

1. Update `version` in `pyproject.toml`.
2. Run `uv lock`, `uv run pytest -q`, `uv run ruff check .`, and `uv build`.
3. Commit and push the release changes.
4. Create a tag matching the version, such as `v0.1.0`.
5. Publish a GitHub Release from that tag.

Publishing the GitHub Release triggers `.github/workflows/publish.yml`. The
workflow tests and builds the project, then the `pypi` job exchanges GitHub's
OIDC identity for a short-lived PyPI credential and uploads `dist/`.

PyPI release files cannot be replaced. If publishing fails after PyPI accepts a
file, increment the version before trying again.

After the GitHub repository exists, add its real Homepage, Repository, and
Issues URLs under `[project.urls]` in `pyproject.toml`.
