"use client";

import { useState, FormEvent } from "react";
import { ReactElement } from "react/React";

import Link from "next/link";

import { useGetModels, useGetClients } from "../hooks";

interface Job {
    model: string,
    server_address: string,
    redis_host: string,
    redis_port: string,
    server_config: Array<ServerConfig>,
    client_info: Array<ClientInfo>,

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
    }
}

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
    const [job, setJob] = useState(makeEmptyJob());

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        try {
            job.server_config = JSON.stringify(job.server_config);

            const response = await fetch("/api/server/job", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(job),
            });

            // Handle response if necessary
            const data = await response.json()
            // ...
        } catch (error) {
            console.error(error);
        }
    }
    return (
        <form onSubmit={onSubmit}>
            <EditJobServerAttributes job={job} setJob={setJob}/>

            <EditJobServerConfig job={job} setJob={setJob}/>

            <EditJobClientsInfo job={job} setJob={setJob}/>

            <button className="btn bg-gradient-primary my-4">Create New Job</button>
        </form>
    );
}

export function EditJobServerAttributes({job, setJob}): ReactElement {
    return (
        <div>
            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="jobModel">
                    Model
                </label>
                <select
                    className="form-control"
                    id="jobModel"
                    value={job.model}
                    onChange={(e) => setJob({...job, model: e.target.value})}
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
                    value={job.server_address}
                    onChange={(e) => setJob({...job, server_address: e.target.value})}
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
                    value={job.redis_host}
                    onChange={(e) => setJob({...job, redis_host: e.target.value})}
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
                    value={job.redis_port}
                    onChange={(e) => setJob({...job, redis_port: e.target.value})}
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

export function EditJobServerConfig({job, setJob}): ReactElement {
    const handleAddServerConfigItem = () => {
        const serverConfig = job.server_config;
        serverConfig.push(makeEmptyServerConfig())
        setJob({...job, server_config: serverConfig});
    };
    return (
        <div>
            <div className="input-group-header">
                <h6>Server Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => handleAddServerConfigItem()}
                >
                    add
                </i>
            </div>
            {job.server_config.map((c, i) => (
                <EditJobServerConfigItem
                    key={i}
                    index={i}
                    job={job}
                    setJob={setJob}
                />
            ))}
        </div>
    );
}

export function EditJobServerConfigItem({ index, job, setJob }): ReactElement {
    const onChangeServerConfig = (attribute, value) => {
        const serverConfig = job.server_config;
        serverConfig[index][attribute] = value;
        setJob({...job, server_config: serverConfig});
    }
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
                        value={job.server_config[index].name}
                        onChange={(e) => onChangeServerConfig("name", e.target.value)}
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
                        value={job.server_config[index].value}
                        onChange={(e) => onChangeServerConfig("value", e.target.value)}
                    />
                </div>
            </div>
        </div>
    );
}

export function EditJobClientsInfo({ job, setJob }): ReactElement {
    const handleAddClientInfo = () => {
        const clientsInfo = job.clients_info;
        clientsInfo.push(makeEmptyClientInfo())
        setJob({...job, clients_info: clientsInfo});
    };

    return (
        <div>
            <div className="input-group-header">
                <h6>Clients Configuration</h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => handleAddClientInfo()}
                >
                    add
                </i>
            </div>
            {job.clients_info.map((c, i) => (
                <EditJobClientsInfoItem
                    key={i}
                    index={i}
                    job={job}
                    setJob={setJob}
                />
            ))}
        </div>
    );
}

export function EditJobClientsInfoItem({ index, job, setJob }): ReactElement {
    const onChangeClientsInfo = (attribute, value) => {
        const clientsInfo = job.clients_info;
        clientsInfo[index][attribute] = value;
        setJob({...job, clients_info: clientsInfo});
    }
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
                    <select
                        className="form-control"
                        id={"jobClientConfigClient" + index}
                        value={job.clients_info[index].client}
                        onChange={(e) => onChangeClientsInfo("client", e.target.value)}
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
                        htmlFor={"jobClientConfigServiceAddress" + index}
                    >
                        Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"jobClientConfigServiceAddress" + index}
                        value={job.clients_info[index].service_address}
                        onChange={(e) => onChangeClientsInfo("service_address", e.target.value)}
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
                        id={"jobClientConfigDataPath" + index}
                        value={job.clients_info[index].data_path}
                        onChange={(e) => onChangeClientsInfo("data_path", e.target.value)}
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
                        id={"jobClientConfigRedisHost" + index}
                        value={job.clients_info[index].redis_host}
                        onChange={(e) => onChangeClientsInfo("redis_host", e.target.value)}
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
                        id={"jobClientConfigRedisPort" + index}
                        value={job.clients_info[index].redis_port}
                        onChange={(e) => onChangeClientsInfo("redis_port", e.target.value)}
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
