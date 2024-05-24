"use client";

import { FormEvent } from "react";
import { ReactElement } from "react/React";
import { useImmer } from "use-immer";
import { produce } from "immer";

import Link from "next/link";

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
    });

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setState(
            produce((newState) => {
                newState.isLoading = true;
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

            const data = await response.json();
        } catch (error) {
            console.error(error);
        }

        setState(
            produce((newState) => {
                newState.isLoading = false;
            }),
        );
    }
    return (
        <form onSubmit={onSubmit}>
            <EditJobServerAttributes state={state} setState={setState} />

            <EditJobServerConfig state={state} setState={setState} />

            <EditJobClientsInfo state={state} setState={setState} />

            <button className="btn bg-gradient-primary my-4">
                {state.isLoading ? "Saving..." : "Save"}
            </button>
        </form>
    );
}

export function EditJobServerAttributes({ state, setState }): ReactElement {
    return (
        <div>
            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="jobModel">
                    Model
                </label>
                <select
                    className="form-control"
                    id="jobModel"
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
                <label className="form-label" htmlFor="jobServerAddress">
                    Server Address
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="jobServerAddress"
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
                <label className="form-label" htmlFor="jobRedisHost">
                    Redis Host
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="jobRedisHost"
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
                <label className="form-label" htmlFor="jobRedisPort">
                    Redis Port
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="jobRedisPort"
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
                        htmlFor={"jobServerConfigName" + index}
                    >
                        Name
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobServerConfigName" + index}
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
                        htmlFor={"jobServerConfigValue" + index}
                    >
                        Value
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobServerConfigValue" + index}
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
                        htmlFor={"jobClientInfoClient" + index}
                    >
                        Client
                    </label>
                    <select
                        className="form-control"
                        id={"jobClientInfoClient" + index}
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
                        htmlFor={"jobClientInfoServiceAddress" + index}
                    >
                        Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobClientInfoServiceAddress" + index}
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
                        htmlFor={"jobClientInfoDataPath" + index}
                    >
                        Data Path
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobClientInfoDataPath" + index}
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
                        htmlFor={"jobClientInfoRedisHost" + index}
                    >
                        Redis Host
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobClientInfoRedisHost" + index}
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
                        htmlFor={"jobClientInfoRedisPort" + index}
                    >
                        Redis Port
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobClientInfoRedisPort" + index}
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
