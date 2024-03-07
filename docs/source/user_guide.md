(user_guide)=

# User Guide

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

### Install Yarn

We use [Yarn](https://yarnpkg.com/) to manage front-end dependencies. Install it on MacOS
using [Homebrew](https://brew.sh/):

```shell
brew install yarn
```

Then install the project dependencies:
```shell
yarn
```

### Pulling Redis' Docker

Redis is used to fetch the metrics reported by servers and clients during their runs.


If you don't have Docker installed, follow [these instructions](https://docs.docker.com/desktop/)
to install it. Then, pull [Redis' official docker image](https://hub.docker.com/_/redis)
(we currently use version 7.2.4):
```shell
docker pull redis:7.2.4
```

## Running the server

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

Use Yarn to run both the back-end and front-end on server mode:

```shell
yarn dev
```

The front-end will be available at `http://localhost:3000`. If you want to access
back-end APIs individually, they will be available at `https://localhost:8000`.

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
uvicorn florist.api.client:app --reload --port 8001
```

The service will be available at `http://localhost:8001`.

# Contributing to the project

If you are a developer of the team or someone who wants to contribute to the project,
please refer to the [CONTRIBUTING.md](https://github.com/VectorInstitute/FLorist/blob/main/CONTRIBUTING.md) file.

Please read and adhere to our [Code of Conduct](https://github.com/VectorInstitute/FLorist/blob/main/CODE_OF_CONDUCT.md)
when making contributions to the project.
