---
hide-toc: true
---

# FLorist

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
