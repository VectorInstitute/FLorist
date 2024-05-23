"use client";

import { useState } from "react";
import { ReactElement } from "react/React";

import Link from "next/link";

import { useGetModels, useGetClients } from "../hooks";

export default function EditJob(): ReactElement {
    return (
        <div className="col-6 align-items-center">
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
    return (
        <form onSubmit={onSubmit}>
            <EditJobServerAttributes />

            <EditJobServerConfig />

            <EditJobClientsConfig />

            <button className="btn bg-gradient-primary my-4">Create New Job</button>
        </form>
    );
}

export function EditJobServerAttributes(): ReactElement {
    return (
        <div>
            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="jobModel">
                    Model
                </label>
                <select className="form-control" id="jobModel">
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

interface ServerConfig {
    name: string;
    value: string;
}

export function EditJobServerConfig(): ReactElement {
    const [serverConfig, setServerConfig] = useState([{ name: "", value: "" }]);

    const handleAddServerConfig = () => {
        setServerConfig([...serverConfig, { name: "", value: "" }]);
    };

    return (
        <div>
            <div className="input-group-header">
                <h6>Server Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => handleAddServerConfig()}
                >
                    add
                </i>
            </div>
            {serverConfig.map((c, i) => (
                <EditJobServerConfigItem
                    key={i}
                    serverConfigItem={c}
                    index={i}
                />
            ))}
        </div>
    );
}

export function EditJobServerConfigItem({
    serverConfigItem,
    index,
}: {
    serverConfigItem: ServerConfig;
    index: string;
}): ReactElement {
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
                        defaultValue={serverConfigItem.name}
                        id={"jobServerConfigName" + index}
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
                        defaultValue={serverConfigItem.value}
                        id={"jobServerConfigValue" + index}
                    />
                </div>
            </div>
        </div>
    );
}

interface ClientConfig {
    client: string;
    service_address: string;
    data_path: string;
    redis_host: string;
    redis_port: string;
}

function make_empty_client_config() {
    return {
        client: "",
        service_address: "",
        data_path: "",
        redis_host: "",
        redis_port: "",
    }
}

export function EditJobClientsConfig(): ReactElement {
    const [clientsConfig, setClientsConfig] = useState([make_empty_client_config()]);

    const handleAddClientConfig = () => {
        setClientsConfig([...clientsConfig, make_empty_client_config()]);
    };

    return (
        <div>
            <div className="input-group-header">
                <h6>Clients Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => handleAddClientConfig()}
                >
                    add
                </i>
            </div>
            {clientsConfig.map((c, i) => (
                <EditJobClientsConfigItem
                    key={i}
                    clientConfig={c}
                    index={i}
                />
            ))}
        </div>
    );
}

export function EditJobClientsConfigItem({
    clientConfig,
    index,
}: {
    clientConfig: ClientConfig;
    index: string;
}): ReactElement {
    return (
        <div className="input-group-flex">
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"jobClientConfigClient" + index}
                    >
                        Client
                    </label>
                    <select className="form-control" id={"jobClientConfigClient" + index}>
                        <option value="empty"></option>
                        <EditJobClientOptions />
                    </select>
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"jobClientConfigServiceAddress" + index}
                    >
                        Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        defaultValue={clientConfig.service_address}
                        id={"jobClientConfigServiceAddress" + index}
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"jobClientConfigDataPath" + index}
                    >
                        Data Path
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        defaultValue={clientConfig.data_path}
                        id={"jobClientConfigDataPath" + index}
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"jobClientConfigRedisHost" + index}
                    >
                        Redis Host
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        defaultValue={clientConfig.redis_host}
                        id={"jobClientConfigRedisHost" + index}
                    />
                </div>
            </div>
            <div className="input-group-two-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label
                        className="form-label"
                        htmlFor={"jobClientConfigRedisPort" + index}
                    >
                        Redis Port
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        defaultValue={clientConfig.redis_port}
                        id={"jobClientConfigRedisPort" + index}
                    />
                </div>
            </div>
        </div>
    );
}

export function EditJobClientOptions(): ReactElement {
    const { data, error, isLoading } = useGetClients();
    if (!data) {
        return null
    }
    return data.map((d, i) => (
        <option key={i} value={d}>
            {d}
        </option>
    ));
}
