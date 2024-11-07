"use client";

import { useSearchParams } from "next/navigation";
import Image from "next/image";

import { useState } from "react";
import { ReactElement } from "react/React";

import { useGetJob } from "../hooks";
import { validStatuses, ClientInfo } from "../definitions";
import loading_gif from "../../assets/img/loading.gif";

export default function JobDetails(): ReactElement {
    return (
        <div className="col-12 align-items-center">
            <JobDetailsHeader />
            <JobDetailsBody />
        </div>
    );
}

export function JobDetailsHeader(): ReactElement {
    return (
        <div className="card-header pb-0 pt-3">
            <h1 className="mt-3 mb-0">Job Details</h1>
        </div>
    );
}

export function JobDetailsBody(): ReactElement {
    const searchParams = useSearchParams();
    const jobId = searchParams.get("id");

    const { data: job, error, isLoading } = useGetJob(jobId);

    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Image id="job-details-loading" src={loading_gif} alt="Loading" height={64} width={64} />
            </div>
        );
    }

    if (!job || error) {
        if (error) {
            console.error(error);
        }
        return (
            <div className="container pt-3 p-0">
                <div className="alert alert-danger text-white" id="job-details-error">
                    Error retrieving job.
                </div>
            </div>
        );
    }

    let totalEpochs = null;
    let localEpochs = null;
    if (job.server_config) {
        const serverConfigJson = JSON.parse(job.server_config);
        totalEpochs = serverConfigJson.n_server_rounds;
        localEpochs = serverConfigJson.local_epochs;
    }

    return (
        <div className="container pt-3 p-0">
            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Job ID:</strong>
                </div>
                <div className="col-sm" id="job-details-id">
                    {job._id}
                </div>
            </div>
            <div className="row pb-2">
                <div className="col-sm-2 align-content-center">
                    <strong className="text-dark">Status:</strong>
                </div>
                <div className="col-sm">
                    <JobDetailsStatus status={job.status} />
                </div>
            </div>
            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Model:</strong>
                </div>
                <div className="col-sm" id="job-details-model">
                    {job.model}
                </div>
            </div>
            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Server Address:</strong>
                </div>
                <div className="col-sm" id="job-details-server-address">
                    {job.server_address}
                </div>
            </div>
            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Redis Host:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-host">
                    {job.redis_host}
                </div>
            </div>
            <div className="row pb-2 mb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Redis Port:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-port">
                    {job.redis_port}
                </div>
            </div>

            <JobProgressBar metrics={job.server_metrics} totalEpochs={totalEpochs} status={job.status} />

            <JobDetailsTable
                Component={JobDetailsServerConfigTable}
                title="Server Configuration"
                data={job.server_config}
            />

            <JobDetailsTable
                Component={JobDetailsClientsInfoTable}
                title="Clients Configuration"
                data={job.clients_info}
                properties={{ localEpochs }}
            />
        </div>
    );
}

export function JobDetailsStatus({ status }: { status: string }): ReactElement {
    let pillClasses = "status-pill text-sm ";
    let iconName;
    let statusDescription;
    switch (String(validStatuses[status])) {
        case validStatuses.NOT_STARTED:
            pillClasses += "alert-info";
            iconName = "radio_button_checked";
            statusDescription = validStatuses[status];
            break;
        case validStatuses.IN_PROGRESS:
            pillClasses += "alert-warning";
            iconName = "sync";
            statusDescription = validStatuses[status];
            break;
        case validStatuses.FINISHED_SUCCESSFULLY:
            pillClasses += "alert-success";
            iconName = "check_circle";
            statusDescription = validStatuses[status];
            break;
        case validStatuses.FINISHED_WITH_ERROR:
            pillClasses += "alert-danger";
            iconName = "error";
            statusDescription = validStatuses[status];
            break;
        default:
            pillClasses += "alert-secondary";
            iconName = "";
            statusDescription = status;
            break;
    }
    return (
        <div className={pillClasses} id="job-details-status">
            <i className="material-icons text-sm" id="job-details-status-icon">
                {iconName}
            </i>
            &nbsp;
            {statusDescription}
        </div>
    );
}

export function JobProgressBar({
    metrics,
    totalEpochs,
    status,
}: {
    metrics: string;
    totalEpochs: number;
    status: status;
}): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    if (!metrics || !totalEpochs) {
        return null;
    }

    const metricsJson = JSON.parse(metrics);

    let endRoundKey;
    if (metricsJson.host_type === "server") {
        endRoundKey = "fit_end";
    }
    if (metricsJson.host_type === "client") {
        endRoundKey = "shutdown";
    }

    let progressPercent = 0;
    if ("rounds" in metricsJson && Object.keys(metricsJson.rounds).length > 0) {
        const lastRound = Math.max(...Object.keys(metricsJson.rounds));
        const lastCompletedRound = endRoundKey in metricsJson ? lastRound : lastRound - 1;
        progressPercent = (lastCompletedRound * 100) / totalEpochs;
    }
    const progressWidth = progressPercent === 0 ? "100%" : `${progressPercent}%`;

    // Clients will not have a status, so we need to set one based on the progress percent
    if (!status) {
        if (progressPercent === 0) {
            status = "NOT_STARTED";
        } else if (progressPercent === 100) {
            status = "FINISHED_SUCCESSFULLY";
        } else {
            status = "IN_PROGRESS";
        }
        // TODO: add error status
    }

    let progressBarClasses = "progress-bar progress-bar-striped";
    switch (String(validStatuses[status])) {
        case validStatuses.IN_PROGRESS:
            progressBarClasses += " bg-warning";
            break;
        case validStatuses.FINISHED_SUCCESSFULLY:
            progressBarClasses += " bg-success";
            break;
        case validStatuses.FINISHED_WITH_ERROR:
            progressBarClasses += " bg-danger";
            break;
        case validStatuses.NOT_STARTED:
        default:
            break;
    }
    if (progressPercent === 0) {
        progressBarClasses += " bg-disabled";
    }

    return (
        <div className="job-progress-bar mb-4">
            <div className="card my-4">
                <div className="card-header pb-0">
                    <strong className="text-dark">Progress:</strong>
                </div>
                <div className="card-body">
                    <div className="row pb-2">
                        <div className="progress col-sm-5">
                            <div
                                className={progressBarClasses}
                                role="progressbar"
                                style={{ width: progressWidth }}
                                aria-valuenow={progressPercent}
                                aria-valuemin="0"
                                aria-valuemax="100"
                            >
                                <strong>{Math.floor(progressPercent)}%</strong>
                            </div>
                        </div>
                        <div className="job-details-toggle col-sm job-expand-button">
                            <a className="btn btn-link" onClick={() => setCollapsed(!collapsed)}>
                                {collapsed ? (
                                    <span>
                                        Expand
                                        <i className="material-icons text-sm">keyboard_arrow_down</i>
                                    </span>
                                ) : (
                                    <span>
                                        Collapse
                                        <i className="material-icons text-sm">keyboard_arrow_up</i>
                                    </span>
                                )}
                            </a>
                        </div>
                    </div>
                    <div className="row pb-2">{!collapsed ? <JobProgressDetails metrics={metricsJson} /> : null}</div>
                </div>
            </div>
        </div>
    );
}

export function JobProgressDetails({ metrics }: { metrics: Object }): ReactElement {
    if (!metrics) {
        return null;
    }

    let fitStartKey;
    let fitEndKey;
    if (metrics.host_type === "server") {
        fitStartKey = "fit_start";
        fitEndKey = "fit_end";
    }
    if (metrics.host_type === "client") {
        fitStartKey = "initialized";
        fitEndKey = "shutdown";
    }

    let elapsedTime = "";
    if (fitStartKey in metrics) {
        const startDate = Date.parse(metrics[fitStartKey]);
        const endDate = fitEndKey in metrics ? Date.parse(metrics[fitEndKey]) : Date.now();
        elapsedTime = getTimeString(endDate - startDate);
    }

    let roundMetricsArray = [];
    if (metrics.rounds) {
        roundMetricsArray = Array(metrics.rounds.length);
        for (const [round, roundMetrics] of Object.entries(metrics.rounds)) {
            roundMetricsArray[parseInt(round) - 1] = roundMetrics;
        }
    }

    return (
        <div className="job-progress-detail">
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Elapsed time:</strong>
                </div>
                <div className="col-sm">{elapsedTime}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Start time:</strong>
                </div>
                <div className="col-sm">{fitStartKey in metrics ? metrics[fitStartKey] : null}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">End time:</strong>
                </div>
                <div className="col-sm">{fitEndKey in metrics ? metrics[fitEndKey] : null}</div>
            </div>

            {Object.keys(metrics).map((name, i) => (
                <JobProgressProperty name={name} value={metrics[name]} key={i} />
            ))}

            {roundMetricsArray.map((roundMetrics, i) => (
                <JobProgressRound roundMetrics={roundMetrics} key={i} index={i} />
            ))}
        </div>
    );
}

export function JobProgressRound({ roundMetrics, index }: { roundMetrics: Object; index: int }): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    if (!roundMetrics) {
        return null;
    }

    return (
        <div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Round {index + 1}</strong>
                </div>
                <div className={`job-round-toggle-${index} col-sm job-expand-button`}>
                    <a className="btn btn-link" onClick={() => setCollapsed(!collapsed)}>
                        {collapsed ? (
                            <span>
                                Expand
                                <i className="material-icons text-sm">keyboard_arrow_down</i>
                            </span>
                        ) : (
                            <span>
                                Collapse
                                <i className="material-icons text-sm">keyboard_arrow_up</i>
                            </span>
                        )}
                    </a>
                </div>
                {!collapsed ? <JobProgressRoundDetails roundMetrics={roundMetrics} key={index} index={index} /> : null}
            </div>
        </div>
    );
}

export function JobProgressRoundDetails({ roundMetrics, index }: { roundMetrics: Object; index: str }): ReactElement {
    if (!roundMetrics) {
        return null;
    }

    let fitElapsedTime = "";
    if ("fit_start" in roundMetrics) {
        const startDate = Date.parse(roundMetrics.fit_start);
        const endDate = "fit_end" in roundMetrics ? Date.parse(roundMetrics.fit_end) : Date.now();
        fitElapsedTime = getTimeString(endDate - startDate);
    }

    let evaluateElapsedTime = "";
    if ("evaluate_start" in roundMetrics) {
        const startDate = Date.parse(roundMetrics.evaluate_start);
        const endDate = "evaluate_end" in roundMetrics ? Date.parse(roundMetrics.evaluate_end) : Date.now();
        evaluateElapsedTime = getTimeString(endDate - startDate);
    }

    return (
        <div className={`job-round-details-${index} job-round-details`}>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Fit elapsed time:</strong>
                </div>
                <div className="col-sm">{fitElapsedTime}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Fit start time:</strong>
                </div>
                <div className="col-sm">{"fit_start" in roundMetrics ? roundMetrics.fit_start : null}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Fit end time:</strong>
                </div>
                <div className="col-sm">{"fit_end" in roundMetrics ? roundMetrics.fit_end : null}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Evaluate elapsed time:</strong>
                </div>
                <div className="col-sm">{evaluateElapsedTime}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Evaluate start time:</strong>
                </div>
                <div className="col-sm">{"evaluate_start" in roundMetrics ? roundMetrics.evaluate_start : null}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Evaluate end time:</strong>
                </div>
                <div className="col-sm">{"evaluate_end" in roundMetrics ? roundMetrics.evaluate_end : null}</div>
            </div>
            {Object.keys(roundMetrics).map((name, i) => (
                <JobProgressProperty name={name} value={roundMetrics[name]} key={i} />
            ))}
        </div>
    );
}

export function JobProgressProperty({ name, value }: { name: string; value: string }): ReactElement {
    if (
        [
            "fit_start",
            "fit_end",
            "evaluate_start",
            "evaluate_end",
            "rounds",
            "host_type",
            "initialized",
            "shutdown",
        ].includes(name)
    ) {
        return null;
    }
    let renderedValue = value;
    if (value.constructor === Array) {
        renderedValue = JSON.stringify(value);
    } else if (value.constructor === Object) {
        renderedValue = Object.keys(value).map((valueName, i) => (
            <JobProgressProperty name={valueName} value={value[valueName]} key={i} />
        ));
    }

    return (
        <div className="row">
            <div className="col-sm-2">
                <strong className="text-dark">{name}:</strong>
            </div>
            <div className="col-sm">{renderedValue}</div>
        </div>
    );
}

export function JobDetailsTable({ Component, title, data, properties }): ReactElement {
    return (
        <div className="row">
            <div className="col-12">
                <div className="card my-4">
                    <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2 col-sm-4">
                        <div className="bg-gradient-primary shadow-primary border-radius-lg pt-4 pb-3">
                            <h6 className="text-white text-capitalize text-nowrap ps-3">{title}</h6>
                        </div>
                    </div>

                    <div className="card-body px-0 pb-2">
                        <div className="table-responsive p-0">
                            <Component data={data} properties={properties} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export function JobDetailsServerConfigTable({ data, properties }: { data: string; properties: Object }): ReactElement {
    const emptyResponse = (
        <div className="container" id="job-details-server-config-empty">
            Empty.
        </div>
    );

    if (!data) {
        return emptyResponse;
    }

    const serverConfigJson = JSON.parse(data);

    if (typeof serverConfigJson != "object" || Array.isArray(serverConfigJson)) {
        return (
            <div className="container" id="job-details-server-config-error">
                Error parsing server configuration.
            </div>
        );
    }

    const serverConfigNames = Object.keys(serverConfigJson);

    if (serverConfigNames.length === 0) {
        return emptyResponse;
    }

    return (
        <table className="table align-items-center mb-0">
            <thead>
                <tr>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Name</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Value</th>
                </tr>
            </thead>
            <tbody>
                {serverConfigNames.map((serverConfigName, i) => (
                    <tr key={i}>
                        <td className="col-sm-2" id={`job-details-server-config-name-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm font-weight-bold">{serverConfigName}</span>
                            </div>
                        </td>
                        <td className="col-sm" id={`job-details-server-config-value-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {serverConfigJson[serverConfigName]}
                                </span>
                            </div>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export function JobDetailsClientsInfoTable({
    data,
    properties,
}: {
    data: Array<ClientInfo>;
    properties: Object;
}): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <table className="table align-items-center mb-0">
            <thead>
                <tr>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Client</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Address</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Data Path</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Redis Host</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Redis Port</th>
                </tr>
            </thead>
            <tbody>
                {data.map((clientInfo, i) => {
                    let additionalClasses = clientInfo.metrics ? "" : "empty-cell";
                    return [
                        <tr className="job-client-details" key={`${i}-details`}>
                            <td className="col-sm" id={`job-details-client-config-client-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.client}</span>
                                </div>
                            </td>
                            <td className="col-sm" id={`job-details-client-config-service-address-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.service_address}</span>
                                </div>
                            </td>
                            <td className="col-sm" id={`job-details-client-config-data-path-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.data_path}</span>
                                </div>
                            </td>
                            <td className="col-sm" id={`job-details-client-config-redis-host-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.redis_host}</span>
                                </div>
                            </td>
                            <td className="col-sm" id={`job-details-client-config-redis-port-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.redis_port}</span>
                                </div>
                            </td>
                        </tr>,
                        <tr id={`job-client-progress-${i}`} key={`${i}-progress`}>
                            <td className={`job-client-progress-label col-sm ${additionalClasses}`}>
                                {clientInfo.metrics ? (
                                    <div className="d-flex flex-column justify-content-center">
                                        <span className="ps-3 text-secondary text-sm">Progress:</span>
                                    </div>
                                ) : null}
                            </td>
                            <td
                                className={`job-client-progress col-sm ${additionalClasses}`}
                                id={`job-details-client-config-progress-${i}`}
                                colSpan="3"
                            >
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">
                                        <JobProgressBar
                                            metrics={clientInfo.metrics}
                                            totalEpochs={properties.localEpochs}
                                        />
                                    </span>
                                </div>
                            </td>
                        </tr>,
                    ];
                })}
            </tbody>
        </table>
    );
}

export function getTimeString(timeInMiliseconds: number): string {
    const hours = Math.floor(timeInMiliseconds / 1000 / 60 / 60);
    const minutes = Math.floor((timeInMiliseconds / 1000 / 60 / 60 - hours) * 60);
    const seconds = Math.floor(((timeInMiliseconds / 1000 / 60 / 60 - hours) * 60 - minutes) * 60);

    let timeString = "";
    if (hours <= 0 && minutes <= 0 && seconds < 10) {
        // Adding the miliseconds if the time is less than 10s
        timeString = `${timeInMiliseconds - 1000 * seconds}ms`;
    }
    if (seconds > 0) {
        const secondsString = seconds < 10 ? `0${seconds}` : `${seconds}`;
        timeString = secondsString + "s " + timeString;
    }
    if (minutes > 0) {
        const minutesString = minutes < 10 ? `0${minutes}` : `${minutes}`;
        timeString = minutesString + "m " + timeString;
    }
    if (hours > 0) {
        const hoursString = hours < 10 ? `0${hours}` : `${hours}`;
        timeString = hoursString + "h " + timeString;
    }

    return timeString.trim();
}
