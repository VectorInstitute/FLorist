# Contributing to AI Engineering Projects

Thanks for your interest in contributing!

To submit PRs, please fill out the PR template along with the PR. If the PR
fixes an issue, don't forget to link the PR to the issue!

## Pre-commit hooks

Once the python virtual environment is setup, you can run pre-commit hooks using:

```bash
pre-commit run --all-files
```

## Development dependencies

To install development dependencies, first you need to create a virtual environment.
The easiest way is by using the [virtualenv](https://pypi.org/project/virtualenv/) package:

```shell
virtualenv venv
source venv/bin/activate
```

We use [Poetry](https://python-poetry.org/) to manage back-end dependencies:

```shell
pip install --upgrade pip poetry
poetry install --with dev
```

We use [Yarn](https://yarnpkg.com/) to manage front-end dependencies. Install it on MacOS
using [Homebrew](https://brew.sh/):

```shell
brew install yarn
```

Then install the project dependencies:
```shell
yarn
```

## Coding guidelines

For code style, we recommend the [google style guide](https://google.github.io/styleguide/pyguide.html).

Pre-commit hooks apply the [black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
code formatting.

For docstrings we use [numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

We also use [flake8](https://flake8.pycqa.org/en/latest/) and [pylint](https://pylint.pycqa.org/en/stable/)
for further static code analysis. The pre-commit hooks show errors which you need
to fix before submitting a PR.

Last but not the least, we use type hints in our code which is then checked using
[mypy](https://mypy.readthedocs.io/en/stable/). Currently, mypy checks are not
strict, but will be enforced more as the API code becomes more stable.
