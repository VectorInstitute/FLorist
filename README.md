# FLorist

A platform to launch federated learning (FL) training jobs.

## Setting up

### Install dependencies

To install the project dependencies, first you need to create a virtual environment.
The easiest way is by using the [virtualenv](https://pypi.org/project/virtualenv/) package:

```shell
virtualenv venv
source venv/bin/activate
```

We use [Poetry](https://python-poetry.org/) to manage back-end dependencies:

```shell
pip install --upgrade pip poetry
poetry install
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

### Running the server

Use Yarn to run both the back-end and front-end on server mode:

```shell
yarn dev
```

The front-end will be available at `http://localhost:3000`. If you want to access
back-end APIs individually, they will be available at `https://localhost:8000`.

### Running the client

To start the client back-end service:

```shell
uvicorn florist.api.client:app --reload --port 8001
```

The service will be available at `http://localhost:8001`.
