---
hide-toc: true
---

# <img src="https://github.com/VectorInstitute/FLorist/assets/11467898/5c7bcdef-311f-4a88-ae72-ed16f76b7c03" alt="FLorist logo" width="40"/> FLorist

```{toctree}
:hidden:

user_guide
api

```

FLorist is a platform to launch and monitor Federated Learning (FL) training jobs. Its goal is
to bridge the gap between state-of-the-art FL algorithm implementations and their applications
by providing a system to easily kick off, orchestrate, manage, collect, and summarize the results
of [FL4Health](https://github.com/VectorInstitute/FL4Health) training jobs.

As Federated Learning has a client and a server side, FLorist also has client and server-side
“modes” to orchestrate the training process on both sides. When FLorist's client long-running
process is started, they will be waiting for instructions from FLorist's server to start
FL clients for training. Once FLorist's server starts the FL server, it sends instructions
to FLorist's clients to start their own FL clients. Then, FLorist's server monitors the FL server
and clients processes while collecting their progress to be displayed in the web UI.

At the end of training, it saves the results in a database and also provide access to the
training artifacts (e.g. model files). For a visual representation of the system, please check
the diagram below.

![system_diagram.png](system_diagram.png)

## Use Cases

### 1. Facilitate the orchestration of FL4Health training process

**Scenario**: The process of training an FL4Health model is manual and cumbersome,
requiring a lot of technical and programming knowledge.

**Steps**:
- Provide an easy-to-use UI to set up the parameters of a training job
- Display the progress and preliminary metrics while training is happening
- Display the results if successful, or centralized error messages
and logs if not
- Make the training artifacts (e.g. models) easily accessible in a centralized place

### 2. Facilitate the use of state-of-the-art FL implementations

**Scenario**: State-of-the-art algorithms implemented in FL4Health are not
easy to be adopted because of the relatively high learning curve.

**Steps**:
- By providing an easy-to-use UI, the learning curve to adopt FL4Health is reduced
- Providing a centralized place to see the progress, access the logs and the
training artifacts also lowers the barrier of adoption
- Having a system where training jobs can be easily restarted with different
parameters facilitates experimentation

### 3. Provide a useful tool to the open source community

**Scenario**: There is a scarcity of tools for orchestrating and managing
FL training jobs in the OSS community.

**Steps**:
- Develop a high-quality, easy-to-use and extensible tool for managing FL
training jobs in FL4Health and later Flower in general
- Use the latest and greatest front-end and back-end technologies and code
practices
- Provide a robust and visually enticing user interface
