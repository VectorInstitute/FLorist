"use client";

import { useState } from 'react';
import { ReactElement } from "react/React";

import { useGetModels } from "./hooks";

export default function NewJob(): ReactElement {
    return (
        <div className="col-6 text-end">
            <NewJobButton />
            <div className="fixed-plugin text-start">
                <div className="card shadow-lg">
                    <NewJobHeader />

                    <hr className="horizontal dark my-1" />

                    <NewJobForm />
                </div>
            </div>
        </div>
    );
}

export function NewJobButton(): ReactElement {
    return (
        <a className="fixed-plugin-button btn bg-gradient-primary mb-0">
            <i className="material-icons text-sm">add</i>
            &nbsp;&nbsp;New Job
        </a>
    );
}

export function NewJobHeader(): ReactElement {
    return (
        <div className="card-header pb-0 pt-3">
            <div className="float-start">
                <h5 className="mt-3 mb-0">New Job</h5>
                <p>Create a new FL training job.</p>
            </div>
            <div className="float-end mt-4">
                <button className="btn btn-link text-dark p-0 fixed-plugin-close-button">
                    <i className="material-icons">clear</i>
                </button>
            </div>
        </div>
    );
}

export function NewJobForm(): ReactElement {
    return (
        <div className="card-body pt-sm-3 pt-0">
            <form className="text-start">

                <div className="input-group input-group-outline mb-3">
                    <label className="form-label form-row" htmlFor="jobModel">
                        Model
                    </label>
                    <select className="form-control" id="jobModel">
                        <option value="empty"></option>
                        <NewJobModelOptions />
                    </select>
                </div>

                <div className="input-group input-group-outline mb-3">
                    <label className="form-label" htmlFor="jobServerAddress">
                        Server Address
                    </label>
                    <input className="form-control" type="text" id="jobServerAddress" />
                </div>

                <div className="input-group input-group-outline mb-3">
                    <label className="form-label" htmlFor="jobRedisHost">
                        Redis Host
                    </label>
                    <input className="form-control" type="text" id="jobRedisHost" />
                </div>

                <div className="input-group input-group-outline mb-3">
                    <label className="form-label" htmlFor="jobRedisPort">
                        Redis Port
                    </label>
                    <input className="form-control" type="text" id="jobRedisPort" />
                </div>

                <NewJobServerConfig />

            </form>
        </div>
    );
}

export function NewJobModelOptions(): ReactElement {
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

export function NewJobServerConfig(): ReactElement {
    const [serverConfig, setServerConfig] = useState([{ key: '', value: '' }]);

    const handleAddServerConfig = () => {
        setServerConfig([...serverConfig, { name: "", value: "" }]);
    };

    return (
        <div>
            <div className="input-group-header">
                <h6 className="mb-0">
                    Server Configuration
                </h6>
                <i
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => handleAddServerConfig()}
                >
                    add
                </i>
            </div>
            <div className="label-group">
                <span>Name</span>
                <span>Value</span>
            </div>
            {serverConfig.map((c, i) => (
                <NewJobServerConfigItem key={i} serverConfigItem={c} index={i} />
            ))}
        </div>
    )
}

export function NewJobServerConfigItem({
    serverConfigItem,
    index,
}: {
    serverConfigItem: ServerConfig;
    index: string;
}): ReactElement {
    return (
        <div className="input-group input-group-outline mb-3 input-group-margin">
            <input className="form-control" type="text" id={"jobServerConfigName" + index} />
            <input className="form-control" type="text" id={"jobServerConfigValue" + index} />
        </div>
    )
}
