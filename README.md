# mock-api

## Installation

```sh
pyinstaller mock-api.spec
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.8+
* Create a virtual environment and install the dependencies

```sh
pip install -r requirements.txt
```

* Activate the virtual environment

```sh
python -m venv .venv
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github project page
 ](https://pages.github.com/) automatically as part each release.

### Releasing

Trigger the [Draft release workflow](https://github.com/moorefu/push it/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/moorefu/push it/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/moorefu/push it/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

This project was generated using the [wolt-python-package-cookiecutter](https://github.com/woltapp/wolt-python-package-cookiecutter) template.
