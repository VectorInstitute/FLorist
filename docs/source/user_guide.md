(user_guide)=

# User Guide

## pyproject.toml file and dependency management

If your project doesn't have a pyproject.toml file, simply copy the one from the
template and update file according to your project.

For managing dependencies, [Poetry](https://python-poetry.org/) is the recommended tool
for our team. Hence, install Poetry to setup the development virtual environment. Poetry
supports [optional dependency groups](https://python-poetry.org/docs/managing-dependencies/#optional-groups)
which help manage dependencies for different parts of development such as `documentation`,
`testing`, etc. The core dependencies are installed using the command:

```bash
python3 -m poetry install
```

Additional dependency groups can be installed using the `--with` flag. For example:

```bash
python3 -m poetry install --with docs,test
```

## documentation

If your project doesn't have documentation, copy the directory named `docs` to the root
directory of your repository. The provided source files use [Furo](https://pradyunsg.me/furo/),
a clean and customisable Sphinx documentation theme.

In order to build the documentation, install the documentation dependencies as mentioned
in the previous section, navigate to the `docs` folder and run the command:

```bash
make html
```

You can configure the documentation by updating the `docs/source/conf.py`. The markdown
files in `docs/source` can be updated to reflect the project's documentation.


## github actions

The template consists of some github action continuous integration workflows that you
can add to your repository.

The available workflows are:

- [code checks](https://github.com/VectorInstitute/aieng-template/blob/main/.github/workflows/code_checks.yml): Static code analysis, code formatting and unit tests
- [documentation](https://github.com/VectorInstitute/aieng-template/blob/main/.github/workflows/docs_deploy.yml): Project documentation including example API reference
- [integration tests](https://github.com/VectorInstitute/aieng-template/blob/main/.github/workflows/integration_tests.yml): Integration tests
- [publish](https://github.com/VectorInstitute/aieng-template/blob/main/.github/workflows/publish.yml):
Publishing python package to PyPI. Create a `PYPI_API_TOKEN` and add it to the
repository's actions [secret variables](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
in order to publish PyPI packages when new software releases are created on Github.

The test workflows also compute coverage and upload code coverage metrics to
[codecov.io](https://app.codecov.io/gh/VectorInstitute/aieng-template). Create a
`CODECOV_TOKEN` and add it to the repository's actions [secret variables](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
