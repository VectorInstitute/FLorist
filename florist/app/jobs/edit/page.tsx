"use client";

import { FormEvent } from "react";
import { ReactElement } from "react/React";
import { useImmer } from "use-immer";
import { produce } from "immer";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useGetModels, useGetClients } from "../hooks";

interface Job {
    model: string;
    server_address: string;
    redis_host: string;
    redis_port: string;
    server_config: Array<ServerConfig>;
    client_info: Array<ClientInfo>;
}

interface ServerConfig {
    name: string;
    value: string;
}

interface ClientInfo {
    client: string;
    service_address: string;
    data_path: string;
    redis_host: string;
    redis_port: string;
}

function makeEmptyJob() {
    return {
        model: "",
        server_address: "",
        redis_host: "",
        redis_port: "",
        server_config: [makeEmptyServerConfig()],
        clients_info: [makeEmptyClientInfo()],
    };
}

function makeEmptyServerConfig() {
    return {
        name: "",
        value: "",
    };
}

function makeEmptyClientInfo() {
    return {
        client: "",
        service_address: "",
        data_path: "",
        redis_host: "",
        redis_port: "",
    };
}

export default function EditJob(): ReactElement {
    return (
        <div className="col-7 align-items-center">
            <EditJobHeader />
            <EditJobForm />
        </div>
    );
}

export function EditJobHeader(): ReactElement {
    return (
        <div className="card-header pb-0 pt-3">
            <div className="float-start">
                <h1 className="mt-3 mb-0">New Job</h1>
                <p>Create a new FL training job</p>
            </div>
        </div>
    );
}

export function EditJobForm(): ReactElement {
    const [state, setState] = useImmer({
        job: makeEmptyJob(),
        isLoading: false,
        savedSuccessfully: false,
        saveError: false,
    });
    const router = useRouter();

    let buttonClasses = "btn my-4 save-btn ";
    if (state.isLoading) {
        buttonClasses += "bg-gradient-secondary disabled";
    } else {
        buttonClasses += "bg-gradient-primary";
    }

    return (
        <form onSubmit={(e) => onSubmitJob(state, setState, router)}>
            <EditJobServerAttributes state={state} setState={setState} />

            <EditJobServerConfig state={state} setState={setState} />

            <EditJobClientsInfo state={state} setState={setState} />

            <button className={buttonClasses}>
                {state.isLoading && !state.savedSuccessfully? "Saving..." : "Save"}
            </button>

            {state.savedSuccessfully ?
                <div className="alert alert-secondary text-white" role="alert">
                    <span className="text-sm">
                        Job saved successfully.
                    </span>
                </div>
            : null}

            {state.saveError ?
                <div className="alert alert-danger alert-dismissible text-white show" role="alert">
                    <span className="text-sm">
                        Error saving job. Please review the information and try again.
                    </span>
                    <button type="button" className="btn-close text-lg py-3 opacity-10" aria-label="Close" onClick={
                        (e) => e.target.parentElement.parentElement.style.display = "none"
                    }>
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
            : null}
        </form>
    );
}

async function onSubmitJob(state, setState, router) {
    event.preventDefault();

    if (state.isLoading) {
        return;
    }

    setState(
        produce((newState) => {
            newState.isLoading = true;
            newState.saveError = false;
            newState.savedSuccessfully = false;
        }),
    );

    try {
        const job = { ...state.job };
        job.server_config = JSON.stringify(job.server_config);

        const response = await fetch("/api/server/job", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(job),
        });

        if (response.status != 201) {
            setState(
                produce((newState) => {
                    newState.isLoading = false;
                    newState.saveError = true;
                })
            );
            console.log(response);
            return;
        }

        setState(
            produce((newState) => {
                newState.savedSuccessfully = true;
            })
        );
        setTimeout(() => router.push("/jobs"), 1000);

    } catch (error) {
        console.error(error);
        setState(
            produce((newState) => {
                newState.isLoading = false;
                newState.saveError = true;
            })
        );
    }
}

export function EditJobServerAttributes({ state, setState }): ReactElement {
    return (
        <div>
            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="job-model">
                    Model
                </label>
                <select
                    className="form-control"
                    id="job-model"
                    value={state.job.model}
                    onChange={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.model = e.target.value;
                            }),
                        )
                    }
                >
                    <option value="empty"></option>
                    <EditJobModelOptions />
                </select>
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label" htmlFor="job-server-address">
                    Server Address
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="job-server-address"
                    value={state.job.server_address}
                    onChange={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.server_address = e.target.value;
                            }),
                        )
                    }
                />
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label" htmlFor="job-redis-host">
                    Redis Host
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="job-redis-host"
                    value={state.job.redis_host}
                    onChange={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.redis_host = e.target.value;
                            }),
                        )
                    }
                />
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label" htmlFor="job-redis-port">
                    Redis Port
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="job-redis-port"
                    value={state.job.redis_port}
                    onChange={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.redis_port = e.target.value;
                            }),
                        )
                    }
                />
            </div>
        </div>
    );
}

export function EditJobModelOptions(): ReactElement {
    const { data, error, isLoading } = useGetModels();
    if (!data) {
        return null;
    }
    return data.map((d, i) => (
        <option key={i} value={d}>
            {d}
        </option>
    ));
}

export function EditJobServerConfig({ state, setState }): ReactElement {
    const addServerConfigItem = produce((newState) => {
        newState.job.server_config.push(makeEmptyServerConfig());
    });
    return (
        <div>
            <div className="input-group-header">
                <h6>Server Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => setState(addServerConfigItem(state))}
                >
                    add
                </i>
            </div>
            {state.job.server_config.map((c, i) => (
                <EditJobServerConfigItem
                    key={i}
                    index={i}
                    state={state}
                    setState={setState}
                />
            ))}
        </div>
    );
}

export function EditJobServerConfigItem({
    index,
    state,
    setState,
}): ReactElement {
    const changeServerConfigAttribute = produce((newState, attribute, value) => {
        newState.job.server_config[index][attribute] = value;
    });
    return (
        <div className="input-group-flex">
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-server-config-name-" + index}
                    >
                        Name
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-server-config-name-" + index}
                        value={state.job.server_config[index].name}
                        onChange={(e) =>
                            setState(
                                changeServerConfigAttribute(
                                    state,
                                    "name",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-server-config-value-" + index}
                    >
                        Value
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-server-config-value-" + index}
                        value={state.job.server_config[index].value}
                        onChange={(e) =>
                            setState(
                                changeServerConfigAttribute(
                                    state,
                                    "value",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
        </div>
    );
}

export function EditJobClientsInfo({ state, setState }): ReactElement {
    const addServerConfigItem = produce((newState) => {
        newState.job.clients_info.push(makeEmptyClientInfo());
    });
    return (
        <div>
            <div className="input-group-header">
                <h6>Clients Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => setState(addServerConfigItem(state))}
                >
                    add
                </i>
            </div>
            {state.job.clients_info.map((c, i) => (
                <EditJobClientsInfoItem
                    key={i}
                    index={i}
                    state={state}
                    setState={setState}
                />
            ))}
        </div>
    );
}

export function EditJobClientsInfoItem({
    index,
    state,
    setState,
}): ReactElement {
    const changeClientInfoAttribute = produce((newState, attribute, value) => {
        newState.job.clients_info[index][attribute] = value;
    });
    return (
        <div className="input-group-flex">
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-client-info-client-" + index}
                    >
                        Client
                    </label>
                    <select
                        className="form-control"
                        id={"job-client-info-client-" + index}
                        value={state.job.clients_info[index].client}
                        onChange={(e) =>
                            setState(
                                changeClientInfoAttribute(
                                    state,
                                    "client",
                                    e.target.value,
                                ),
                            )
                        }
                    >
                        <option value="empty"></option>
                        <EditJobClientOptions />
                    </select>
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-client-info-service-address-" + index}
                    >
                        Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-service-address-" + index}
                        value={state.job.clients_info[index].service_address}
                        onChange={(e) =>
                            setState(
                                changeClientInfoAttribute(
                                    state,
                                    "service_address",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-client-info-data-path-" + index}
                    >
                        Data Path
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-data-path-" + index}
                        value={state.job.clients_info[index].data_path}
                        onChange={(e) =>
                            setState(
                                changeClientInfoAttribute(
                                    state,
                                    "data_path",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-client-info-redis-host-" + index}
                    >
                        Redis Host
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-redis-host-" + index}
                        value={state.job.clients_info[index].redis_host}
                        onChange={(e) =>
                            setState(
                                changeClientInfoAttribute(
                                    state,
                                    "redis_host",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"job-client-info-redis-port-" + index}
                    >
                        Redis Port
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-redis-port-" + index}
                        value={state.job.clients_info[index].redis_port}
                        onChange={(e) =>
                            setState(
                                changeClientInfoAttribute(
                                    state,
                                    "redis_port",
                                    e.target.value,
                                ),
                            )
                        }
                    />
                </div>
            </div>
        </div>
    );
}

export function EditJobClientOptions(): ReactElement {
    const { data, error, isLoading } = useGetClients();
    if (!data) {
        return null;
    }
    return data.map((d, i) => (
        <option key={i} value={d}>
            {d}
        </option>
    ));
}
