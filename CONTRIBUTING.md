# Contributing to FLorist

Thanks for your interest in contributing!

To submit PRs, please fill out the PR template along with the PR. If the PR
fixes an issue, don't forget to link the PR to the issue!

## Setting up

### Development dependencies

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

Then install the project dependencies in development mode:
```shell
yarn -D
```

### Pre-commit hooks

Once the python virtual environment is setup, you can run pre-commit hooks using:

```bash
pre-commit run --all-files
```

### Pulling Redis' Docker

[Redis](https://redis.io/) is used to fetch the metrics reported by servers and clients during their runs.


If you don't have Docker installed, follow [these instructions](https://docs.docker.com/desktop/)
to install it. Then, pull [Redis' official docker image](https://hub.docker.com/_/redis)
(we currently use version 7.2.4):

```shell
docker pull redis:7.2.4
```

### Pulling MongoDB's Docker

[MongoDB](https://www.mongodb.com) is used to store information about the training jobs.

If you don't have Docker installed, follow [these instructions](https://docs.docker.com/desktop/)
to install it. Then, pull [MongoDB' official docker image](https://hub.docker.com/_/mongo)
(we currently use version 7.0.8):
```shell
docker pull mongo:7.0.8
```

## Running the server

### Start MongoDB's instance

If it's your first time running it, create a container and run it with the command below:
```shell
docker run --name mongodb-florist -d -p 27017:27017 mongo:7.0.8
```

From the second time on, you can just start it:
```shell
docker start mongodb-florist
```

### Start server's Redis instance

If it's your first time running it, create a container and run it with the command below:
```shell
docker run --name redis-florist-server -d -p 6379:6379 redis:7.2.4 redis-server --save 60 1 --loglevel warning
```

From the second time on, you can just start it:
```shell
docker start redis-florist-server
```

### Start back-end and front-end servers

Use Yarn to run both the back-end and front-end on production server mode:

```shell
yarn dev
```

The front-end will be available at `http://localhost:3000`. If you want to access
back-end APIs individually, they will be available at `https://localhost:8000`.

Upon first access, you will be redirected to the `/login` page to enter a password.
The default password is `admin` and you will be prompted to change it on first login.
Changing the password to something different than the default is required, all API calls
will fail otherwise.

## Running the client

### Start client's Redis instance

If it's your first time running it, create a container and run it with the command below:
```shell
docker run --name redis-florist-client -d -p 6380:6379 redis:7.2.4 redis-server --save 60 1 --loglevel warning
```

From the second time on, you can just start it:
```shell
docker start redis-florist-client
```

### Start back-end and front-end servers

To start the client back-end service:

```shell
python -m uvicorn florist.api.client:app --reload --port 8001
```

The service will be available at `http://localhost:8001`.

Aditionally, in order to have a client fully up and running, you will need to change the
default password to something else. To do so, go to `http://localhost:8001/change-password/index.html`
and input the new password. The default password is `admin`. Changing the password
to something different than the default is required, all API calls will fail otherwise.
After that, the password will need to be shared with the server for authentication.


## Running the tests

To run the python unit tests, simply execute:
```shell
pytest florist/tests/unit
```

To run the nextjs unit tests, simply execute:

```shell
yarn unit-test
```

To run the integration tests, first make sure you:
- Have a Redis server running on your local machine on port 6379 by following [these instructions](CONTRIBUTING.md#start-servers-redis-instance).
- Have a MongoDB server running on your local machine on port 27017 by following [these instructions](CONTRIBUTING.md#start-mongodbs-instance).

Then execute:
```shell
pytest florist/tests/integration
```

## Building the Docker images

To build the Docker images, you will use the [Dockerfile.client](Dockerfile.client) file for
the client image and [Dockerfile.server](Dockerfile.server) file for the server image.

You can run the following commands to build them:

```shell
docker build -f Dockerfile.client -t florist-client .
docker build -f Dockerfile.server -t florist-server .
```

To start those images individually into containers, you can use the commands below:

```shell
docker run -p 8001:8001 florist-client
docker run -p 3000:3000 florist-server
```

## Coding guidelines

For code style, we recommend the [PEP 8 style guide](https://peps.python.org/pep-0008/).

For docstrings we use [numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and static code
analysis. Ruff checks various rules including [flake8](https://docs.astral.sh/ruff/faq/#how-does-ruff-compare-to-flake8). The pre-commit hooks
show errors which you need to fix before submitting a PR.

Last but not the least, we use type hints in our code which is then checked using
[mypy](https://mypy.readthedocs.io/en/stable/).

## Documentation

Backend code API documentation can be found at https://vectorinstitute.github.io/FLorist/.

Backend REST API documentation can be found at https://localhost:8000/docs once the server
is running locally.
