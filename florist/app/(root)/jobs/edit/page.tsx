"use client";
import yaml from "js-yaml";

import { useRef } from "react";
import { ReactElement } from "react";
import { useImmer } from "use-immer";
import { Draft, produce } from "immer";

import { useRouter } from "next/navigation";
import { useGetModels, useGetClients, useGetStrategies, useGetOptimizers } from "../hooks";
import { usePost } from "../../../hooks";
import { Job, ServerConfig, ServerConfigDict, ClientInfo } from "../definitions";
import { hashWord } from "../../../auth";

export function makeEmptyJob(): Job {
    return {
        model: "",
        strategy: "",
        optimizer: "",
        server_address: "",
        redis_address: "",
        server_config: [makeEmptyServerConfig()],
        client: "",
        clients_info: [makeEmptyClientInfo()],
    };
}

export function makeEmptyServerConfig(): ServerConfig {
    return {
        name: "",
        value: "",
    };
}

export function makeEmptyClientInfo(): ClientInfo {
    return {
        service_address: "",
        data_path: "",
        redis_address: "",
        hashed_password: "",
    };
}

interface EditJobState {
    job: Job;
}

type SetState = (recipe: (draft: Draft<EditJobState>) => void) => void;
type Hook = (...args: any[]) => { data: string[] };

function formatServerConfig(serverConfig: Array<ServerConfig>): string {
    const serverConfigDict: ServerConfigDict = {};
    for (let sc of serverConfig) {
        serverConfigDict[sc.name] = sc.value;
    }
    return JSON.stringify(serverConfigDict);
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
    const [state, setState] = useImmer<EditJobState>({ job: makeEmptyJob() });
    const router = useRouter();
    const { post, response, isLoading, error } = usePost();

    async function onSubmitJob(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (isLoading) {
            // Preventing double submit if already in progress
            return;
        }

        const job = {
            ...state.job,
            // Server config is a json string, so changing it here before sending the data over
            server_config: formatServerConfig(state.job.server_config),
            // The client password is hashed here before sending the data over
            clients_info: state.job.clients_info.map((client) => ({
                ...client,
                hashed_password: hashWord(client.hashed_password),
            })),
        };
        await post("/api/server/job", JSON.stringify(job));
    }

    if (response) {
        // If the response object is populated, it means it has completed the
        //post request successfully. Then, wait 1s and redirect to the list jobs page
        setTimeout(() => router.push("/jobs"), 1000);
    }

    let buttonClasses = "btn my-4 save-btn ";
    if (isLoading || response) {
        // If is loading or if a successful response has been received,
        // disable the button to avoid double submit.
        buttonClasses += "bg-gradient-secondary disabled";
    } else {
        buttonClasses += "bg-gradient-primary";
    }

    return (
        <form onSubmit={(e) => onSubmitJob(e)}>
            <EditJobServerAttributes state={state} setState={setState} />

            <EditJobServerConfig state={state} setState={setState} />

            <EditJobSelectClient state={state} setState={setState} />

            <EditJobClientsInfo state={state} setState={setState} />

            <button id="job-post" className={buttonClasses}>
                {isLoading ? "Saving..." : "Save"}
            </button>

            {response ? ( // Show the success alert if it has a successful response
                <div id="job-saved-successfully" className="alert alert-secondary text-white" role="alert">
                    <span className="text-sm">Job saved successfully.</span>
                </div>
            ) : null}

            {error ? ( // Show the error alert if it has error
                <div id="job-save-error" className="alert alert-danger alert-dismissible text-white show" role="alert">
                    <span className="text-sm">Error saving job. Please review the information and try again.</span>
                    <button
                        type="button"
                        className="btn-close text-lg py-3 opacity-10"
                        aria-label="Close"
                        onClick={(e) => {
                            const target = e.target as HTMLElement;
                            const parentElement = target.parentElement;
                            if (parentElement && parentElement.parentElement) {
                                parentElement.parentElement.style.display = "none";
                            }
                        }}
                    >
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
            ) : null}
        </form>
    );
}

export function EditJobServerAttributes({
    state,
    setState,
}: {
    state: EditJobState;
    setState: SetState;
}): ReactElement {
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
                        setState((draft: Draft<EditJobState>) => {
                            draft.job.model = e.target.value;
                        })
                    }
                >
                    <option disabled={true} selected={true} value={""}></option>
                    <EditJobSelectOptions hook={useGetModels} />
                </select>
                <label className="select-caret" htmlFor="job-model">
                    &#9660;
                </label>
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="job-strategy">
                    Strategy
                </label>
                <select
                    className="form-control"
                    id="job-strategy"
                    value={state.job.strategy}
                    onChange={(e) =>
                        setState((draft: Draft<EditJobState>) => {
                            draft.job.strategy = e.target.value;
                        })
                    }
                >
                    <option disabled={true} selected={true} value={""}></option>
                    <EditJobSelectOptions hook={useGetStrategies} />
                </select>
                <label className="select-caret" htmlFor="job-strategy">
                    &#9660;
                </label>
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label form-row" htmlFor="job-optimizer">
                    Optimizer
                </label>
                <select
                    className="form-control"
                    id="job-optimizer"
                    value={state.job.optimizer}
                    onChange={(e) =>
                        setState((draft: Draft<EditJobState>) => {
                            draft.job.optimizer = e.target.value;
                        })
                    }
                >
                    <option disabled={true} selected={true} value={""}></option>
                    <EditJobSelectOptions hook={useGetOptimizers} />
                </select>
                <label className="select-caret" htmlFor="job-optimizer">
                    &#9660;
                </label>
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
                        setState((draft: Draft<EditJobState>) => {
                            draft.job.server_address = e.target.value;
                        })
                    }
                />
            </div>

            <div className="input-group input-group-outline gray-input-box mb-3">
                <label className="form-label" htmlFor="job-redis-address">
                    Redis Address
                </label>
                <input
                    className="form-control"
                    type="text"
                    id="job-redis-address"
                    value={state.job.redis_address}
                    onChange={(e) =>
                        setState((draft: Draft<EditJobState>) => {
                            draft.job.redis_address = e.target.value;
                        })
                    }
                />
            </div>
        </div>
    );
}

export function EditJobSelectClient({ state, setState }: { state: EditJobState; setState: SetState }): ReactElement {
    return (
        <div id="job-client-field" className="input-group input-group-outline gray-input-box mb-3">
            <label className="form-label form-row" htmlFor="job-client">
                Client
            </label>
            <select
                className="form-control"
                id="job-client"
                value={state.job.client}
                onChange={(e) =>
                    setState((draft: Draft<EditJobState>) => {
                        draft.job.client = e.target.value;
                    })
                }
                disabled={state.job.strategy ? false : true}
            >
                <option disabled={true} selected={true} value={""}></option>
                <EditJobSelectOptions hook={useGetClients} params={{ strategy: state.job.strategy }} />
            </select>
            <label className="select-caret" htmlFor="job-client">
                &#9660;
            </label>
        </div>
    );
}

export function EditJobSelectOptions({ hook, params }: { hook: Hook; params?: object }): ReactElement {
    const { data } = hook(params);

    if (!data) {
        return <></>;
    }
    return (
        <>
            {data.map((d, i) => (
                <option key={i} value={d}>
                    {d}
                </option>
            ))}
        </>
    );
}

export function EditJobServerConfig({ state, setState }: { state: EditJobState; setState: SetState }): ReactElement {
    const addServerConfigItem = produce((newState) => {
        newState.job.server_config.push(makeEmptyServerConfig());
    });
    return (
        <div id="job-server-config">
            <div className="input-group-header">
                <h6>Server Configuration</h6>

                <EditJobServerConfigUploader state={state} setState={setState} />

                <i
                    id="job-server-config-add"
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => setState(addServerConfigItem(state))}
                >
                    add
                </i>
            </div>
            {state.job.server_config.map((c, i) => (
                <EditJobServerConfigItem key={i} index={i} state={state} setState={setState} />
            ))}
        </div>
    );
}

export function EditJobServerConfigUploader({
    state,
    setState,
}: {
    state: EditJobState;
    setState: SetState;
}): ReactElement {
    const buttonRef = useRef<HTMLInputElement>(null);

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            const fileText = await file.text();

            let data;
            if (file.name.endsWith(".json")) {
                data = JSON.parse(fileText);
            } else if (file.name.endsWith(".yaml") || file.name.endsWith(".yml")) {
                data = yaml.load(fileText);
            } else {
                console.error(`file extension not supported: ${file.name}`);
                return;
            }

            const importedServerConfig = [];
            for (let property of Object.keys(data)) {
                const serverConfigItem = makeEmptyServerConfig();
                serverConfigItem.name = property;
                serverConfigItem.value = data[property];
                importedServerConfig.push(serverConfigItem);
            }

            const setServerConfig = produce((newState, newServerConfig) => {
                newState.job.server_config = newServerConfig;
            });
            setState(setServerConfig(state, importedServerConfig));
        }
    };

    return (
        <div>
            <a
                id="job-server-config-import"
                className="btn btn-link"
                title="Import Server Config as JSON or YAML"
                onClick={() => buttonRef.current?.click()}
            >
                <i className="material-icons">upload</i>
                Import JSON or YAML
            </a>
            <input
                type="file"
                ref={buttonRef}
                id="job-server-config-uploader"
                onChange={handleFileUpload}
                accept=".json,.yaml,.yml,application/json,application/x-yaml,text/yaml"
            />
        </div>
    );
}

export function EditJobServerConfigItem({
    index,
    state,
    setState,
}: {
    index: number;
    state: EditJobState;
    setState: SetState;
}): ReactElement {
    const changeServerConfigAttribute = produce((newState, attribute, value) => {
        newState.job.server_config[index][attribute] = value;
    });

    let nameFieldClasses = "input-group input-group-outline gray-input-box mb-3 ";
    if (state.job.server_config[index].name) {
        nameFieldClasses += "is-filled";
    }

    let valueFieldClasses = "input-group input-group-outline gray-input-box mb-3 ";
    if (state.job.server_config[index].value) {
        valueFieldClasses += "is-filled";
    }

    return (
        <div className="input-group-flex">
            <div className="input-group-column">
                <div className={nameFieldClasses}>
                    <label className="form-label" htmlFor={"job-server-config-name-" + index}>
                        Name
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-server-config-name-" + index}
                        value={state.job.server_config[index].name}
                        onChange={(e) => setState(changeServerConfigAttribute(state, "name", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column">
                <div className={valueFieldClasses}>
                    <label className="form-label" htmlFor={"job-server-config-value-" + index}>
                        Value
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-server-config-value-" + index}
                        value={state.job.server_config[index].value}
                        onChange={(e) => setState(changeServerConfigAttribute(state, "value", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column-action">
                <i
                    id={"job-server-config-remove-" + index}
                    className="material-icons opacity-10 input-group-action"
                    onClick={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.server_config.splice(index, 1);
                            }),
                        )
                    }
                >
                    remove
                </i>
            </div>
        </div>
    );
}

export function EditJobClientsInfo({ state, setState }: { state: EditJobState; setState: SetState }): ReactElement {
    const addServerConfigItem = produce((newState) => {
        newState.job.clients_info.push(makeEmptyClientInfo());
    });
    return (
        <div id="job-clients-info">
            <div className="input-group-header">
                <h6>Clients Configuration</h6>
                <i
                    id="job-clients-info-add"
                    className="material-icons opacity-10 input-group-action"
                    onClick={() => setState(addServerConfigItem(state))}
                >
                    add
                </i>
            </div>
            {state.job.clients_info.map((c, i) => (
                <EditJobClientsInfoItem key={i} index={i} state={state} setState={setState} />
            ))}
        </div>
    );
}

export function EditJobClientsInfoItem({
    index,
    state,
    setState,
}: {
    index: number;
    state: EditJobState;
    setState: SetState;
}): ReactElement {
    const changeClientInfoAttribute = produce((newState, attribute, value) => {
        newState.job.clients_info[index][attribute] = value;
    });
    return (
        <div className="input-group-flex">
            <div className="input-group-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label className="form-label" htmlFor={"job-client-info-service-address-" + index}>
                        Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-service-address-" + index}
                        value={state.job.clients_info[index].service_address}
                        onChange={(e) => setState(changeClientInfoAttribute(state, "service_address", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label className="form-label" htmlFor={"job-client-info-data-path-" + index}>
                        Data Path
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-data-path-" + index}
                        value={state.job.clients_info[index].data_path}
                        onChange={(e) => setState(changeClientInfoAttribute(state, "data_path", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label className="form-label" htmlFor={"job-client-info-redis-address-" + index}>
                        Redis Address
                    </label>
                    <input
                        className="form-control"
                        type="text"
                        id={"job-client-info-redis-address-" + index}
                        value={state.job.clients_info[index].redis_address}
                        onChange={(e) => setState(changeClientInfoAttribute(state, "redis_address", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column">
                <div className="input-group input-group-outline gray-input-box mb-3">
                    <label className="form-label" htmlFor={"job-client-info-password-" + index}>
                        Password
                    </label>
                    <input
                        className="form-control"
                        type="password"
                        id={"job-client-info-password-" + index}
                        value={state.job.clients_info[index].hashed_password}
                        onChange={(e) => setState(changeClientInfoAttribute(state, "hashed_password", e.target.value))}
                    />
                </div>
            </div>
            <div className="input-group-column-action">
                <i
                    id={"job-client-info-remove-" + index}
                    className="material-icons opacity-10 input-group-action"
                    onClick={(e) =>
                        setState(
                            produce((newState) => {
                                newState.job.clients_info.splice(index, 1);
                            }),
                        )
                    }
                >
                    remove
                </i>
            </div>
        </div>
    );
}
