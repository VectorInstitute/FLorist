# <img src="https://github.com/VectorInstitute/FLorist/assets/11467898/5c7bcdef-311f-4a88-ae72-ed16f76b7c03" alt="FLorist logo" width="40"/> FLorist

FLorist is a platform to launch and monitor Federated Learning (FL) training jobs. Its goal is to bridge the gap between state-of-the-art FL algorithm implementations and their applications by providing a system to easily kick off, orchestrate, manage, collect, and summarize the results of FL4Health training jobs.

For a technical deep dive, visit our [documentation](https://vectorinstitute.github.io/FLorist/).

## Running FLorist with Docker

The easiest way to get FLorist up and running is to run the Docker images.

### 1. Installing Docker

In case you don't have Docker installed, install it with the guide below:
https://docs.docker.com/desktop/

The FLorist Docker images are going to be located at [floristdocker/florist](https://hub.docker.com/repository/docker/floristdocker/florist/general) in Docker Hub.

### 2. Start the client container

To start the client container, download the [docker-compose-client.yaml](docker-compose-client.yaml)
file and run the command below:

```shell
docker compose -f docker-compose-client.yaml up
```

That command will start the client's docker image, which will run the service on
port `8001`. The authentication service is configured with a default password `admin`.
You will only be able to successfully authenticate to the client if you change the
default password, which you can do at the URL below:

```
http://localhost:8001/change-password/index.html
```

### 3. Start the server containers

To start the server containers, download the [docker-compose-server.yaml](docker-compose-server.yaml)
file and run the command below:

```shell
docker compose -f docker-compose-server.yaml up
```

That command will start 3 containers:

1. A MongoDB container, called `florist-mongodb` at port `27017`, which serves as
the application database.
2. A Redis container, called `florist-redis` at port `6379`, which serves as
the communication layer between FLorist and the federated learning clients and
servers.
3. The FLorist server service itself, at port `3000`.

Upon first access to the URL below, the UI will prompt you to authenticate with
the default password (`admin`). Right after it will ask you to change that
password in order to keep using the service.

```
http://localhost:3000/
```

### 4. Kicking off training jobs

Once you access the Jobs page, you will need to fill up a few network addresses.
In the Docker configuration, those are the following addresses that will work if
they are all being run within the same machine:

- Server Address: `florist-server:8080` (or any other port between 8080-8200)
- Redis Address: `florist-redis:6379`
- Client Address: `florist-client:8001` (or any other port that you have started the client with)

Please also refer to te screenshot below for a sample configuration:

<img width="876" height="901" alt="Image" src="https://github.com/user-attachments/assets/801bba42-e204-4508-8a9f-94d5c125b7bc" />

## Running FLorist from source

In case you want to run FLorist from the source code, please follow the steps in
our [CONTRIBUTING.md](CONTRIBUTING.md) guide.

# Contributing

If you are interested in contributing to the library, please see [CONTRIBUTING.md](CONTRIBUTING.md).
This file contains many details around contributing to the code base, including development
practices, code checks, tests, and more.
