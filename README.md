# <img src="https://github.com/VectorInstitute/FLorist/assets/11467898/5c7bcdef-311f-4a88-ae72-ed16f76b7c03" alt="FLorist logo" width="40"/> FLorist

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

### Install Yarn

We use [Yarn](https://yarnpkg.com/) to manage front-end dependencies. Install it on MacOS
using [Homebrew](https://brew.sh/). Also make sure install Node in case you don't have it.

```shell
brew install node
brew install yarn
```

Then install the project dependencies in production mode:
```shell
yarn --prod
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
yarn prod
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

# Contributing

If you are interested in contributing to the library, please see [CONTRIBUTING.MD](CONTRIBUTING.md).
This file contains many details around contributing to the code base, including development
practices, code checks, tests, and more.


<!--
TODO: change the readme to this:
docker build -f Dockerfile.client -t florist-client .
docker run -p 8001:8001 florist-client

docker build -f Dockerfile.server -t florist-server .
docker run -p 3000:3000 florist-server
-->
