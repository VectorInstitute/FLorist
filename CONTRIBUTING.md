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
poetry install --with test
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

Install Redis by following [these instructions](README.md#pulling-redis-docker).

Then, run the server and client's Redis instance by following
[these instructions](README.md#start-servers-redis-instance) and
[these instructions](README.md#start-clients-redis-instance) respectively.

## Running the tests

To run the unit tests, simply execute:
```shell
pytest florist/tests/unit
```

To run the integration tests, first make sure you have a Redis server running on your
local machine on port 6379, then execute:
```shell
pytest florist/tests/integration
```

## Coding guidelines

For code style, we recommend the [PEP 8 style guide](https://peps.python.org/pep-0008/).

For docstrings we use [numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and static code
analysis. Ruff checks various rules including [flake8](https://docs.astral.sh/ruff/faq/#how-does-ruff-compare-to-flake8). The pre-commit hooks show errors which you need to fix before submitting a PR.

Last but not the least, we use type hints in our code which is then checked using
[mypy](https://mypy.readthedocs.io/en/stable/).
