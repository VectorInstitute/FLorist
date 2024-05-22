"use client";

import { useState } from "react";
import { ReactElement } from "react/React";

import { useGetModels } from "../hooks";

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
        <div className="card-body pt-sm-3 pt-0">
            <form className="text-start">
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

                <EditJobServerConfig />
            </form>
        </div>
    );
}

export function EditJobModelOptions(): ReactElement {
    const { data, error, isLoading } = useGetModels();
    if (data) {
        return data.map((d, i) => (
            <option key={i} value={d}>
                {d}
            </option>
        ));
    }
    return null;
}

interface ServerConfig {
    name: string;
    value: string;
}

export function EditJobServerConfig(): ReactElement {
    const [serverConfig, setServerConfig] = useState([{ key: "", value: "" }]);

    const handleAddServerConfig = () => {
        setServerConfig([...serverConfig, { name: "", value: "" }]);
    };

    return (
        <div>
            <div className="input-group-header">
                <h6 className="mb-0">Server Configuration</h6>
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
                        id={"jobServerConfigValue" + index}
                    />
                </div>
            </div>
        </div>
    );
}
