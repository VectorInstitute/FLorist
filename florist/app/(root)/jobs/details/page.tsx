"use client";

import { useSearchParams } from "next/navigation";
import Image from "next/image";

import { useState } from "react";
import type { ReactElement } from "react";

import { useGetJob, getServerLogsKey, getClientLogsKey, useSWRWithKey } from "../hooks";
import { validStatuses, ClientInfo, Metrics, RoundMetrics, JobDetailsProperties } from "../definitions";
import loading_gif from "../../../assets/img/loading.gif";

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

    if (!jobId) {
        return (
            <div className="container pt-3 p-0">
                <div className="alert alert-danger text-white">Missing job ID.</div>
            </div>
        );
    }

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
    if (job.server_config) {
        const serverConfigJson = JSON.parse(job.server_config);
        totalEpochs = serverConfigJson.n_server_rounds;
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
                    <strong className="text-dark">Strategy:</strong>
                </div>
                <div className="col-sm" id="job-details-strategy">
                    {job.strategy}
                </div>
            </div>
            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Optimizer:</strong>
                </div>
                <div className="col-sm" id="job-details-optimizer">
                    {job.optimizer}
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
                    <strong className="text-dark">Redis Address:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-address">
                    {job.redis_address}
                </div>
            </div>
            {job.error_message ? (
                <div className="row pb-2 mb-2">
                    <div className="col-sm-2">
                        <strong className="text-dark">Error:</strong>
                    </div>
                    <div className="col-sm" id="job-details-error-message">
                        {job.error_message}
                    </div>
                </div>
            ) : null}

            <JobProgressBar
                metrics={job.server_metrics}
                totalEpochs={totalEpochs}
                jobStatus={job.status}
                jobId={job._id}
            />

            <JobDetailsTable
                Component={JobDetailsServerConfigTable}
                title="Server Configuration"
                data={job.server_config}
                properties={{}}
            />

            <div className="row pb-2">
                <div className="col-sm-2">
                    <strong className="text-dark">Client:</strong>
                </div>
                <div className="col-sm" id="job-details-client">
                    {job.client}
                </div>
            </div>

            <JobDetailsTable
                Component={JobDetailsClientsInfoTable}
                title="Clients Configuration"
                data={job.clients_info}
                properties={{ totalEpochs, jobStatus: job.status, jobId: job._id }}
            />
        </div>
    );
}

export function JobDetailsStatus({ status }: { status: string }): ReactElement {
    let pillClasses = "status-pill text-sm ";
    let iconName;
    let statusDescription;
    const statusKey = status as keyof typeof validStatuses;
    switch (validStatuses[statusKey]) {
        case validStatuses.NOT_STARTED:
            pillClasses += "alert-info";
            iconName = "radio_button_checked";
            statusDescription = validStatuses[statusKey];
            break;
        case validStatuses.IN_PROGRESS:
            pillClasses += "alert-warning";
            iconName = "sync";
            statusDescription = validStatuses[statusKey];
            break;
        case validStatuses.FINISHED_SUCCESSFULLY:
            pillClasses += "alert-success";
            iconName = "check_circle";
            statusDescription = validStatuses[statusKey];
            break;
        case validStatuses.FINISHED_WITH_ERROR:
            pillClasses += "alert-danger";
            iconName = "error";
            statusDescription = validStatuses[statusKey];
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
    jobStatus,
    jobId,
    clientIndex,
}: {
    metrics: string;
    totalEpochs: number;
    jobStatus: keyof typeof validStatuses;
    jobId: string;
    clientIndex?: number;
}): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    if (!metrics || !totalEpochs) {
        return <></>;
    }

    const metricsJson = JSON.parse(metrics);

    let endRoundKey;
    if (metricsJson.host_type === "server") {
        endRoundKey = "eval_round_end";
    } else if (metricsJson.host_type === "client") {
        endRoundKey = "round_end";
    } else {
        console.error(`JobProgressBar: Host type '${metricsJson.host_type}' not supported.`);
        return <></>;
    }

    let progressPercent = 0;
    if ("rounds" in metricsJson && Object.keys(metricsJson.rounds).length > 0) {
        const lastRound = Math.max(...Object.keys(metricsJson.rounds).map(Number));
        const lastCompletedRound = endRoundKey in metricsJson.rounds[lastRound] ? lastRound : lastRound - 1;
        progressPercent = (lastCompletedRound * 100) / totalEpochs;
    }
    const progressWidth = progressPercent === 0 ? "100%" : `${progressPercent}%`;

    // Clients will not have a status, so we need to set one based on
    // the server status and progress percent
    let status = jobStatus as keyof typeof validStatuses;
    if (metricsJson.host_type === "client") {
        if (
            validStatuses[status] !== validStatuses.FINISHED_SUCCESSFULLY &&
            validStatuses[status] !== validStatuses.FINISHED_WITH_ERROR
        ) {
            if (progressPercent === 100) {
                status = "FINISHED_SUCCESSFULLY";
            } else {
                status = "IN_PROGRESS";
            }
        }
    }

    let progressBarClasses = "progress-bar progress-bar-striped";
    switch (validStatuses[status]) {
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
                                aria-valuemin={0}
                                aria-valuemax={100}
                            >
                                <strong>{Math.floor(progressPercent)}%</strong>
                            </div>
                        </div>
                        <div className="job-details-toggle col-sm job-details-button">
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
                    <div className="row pb-2">
                        {!collapsed ? (
                            <JobProgressDetails
                                metrics={metricsJson}
                                jobId={jobId}
                                clientIndex={clientIndex}
                                status={status}
                            />
                        ) : null}
                    </div>
                </div>
            </div>
        </div>
    );
}

export function JobProgressDetails({
    metrics,
    jobId,
    status,
    clientIndex,
}: {
    metrics: Metrics;
    jobId: string;
    status: string;
    clientIndex?: number;
}): ReactElement {
    const [showLogs, setShowLogs] = useState(false);

    if (!metrics) {
        return <></>;
    }

    let fitStartKey;
    let fitEndKey;
    if (metrics.host_type === "server") {
        fitStartKey = "fit_start";
        fitEndKey = "fit_end";
    } else if (metrics.host_type === "client") {
        fitStartKey = "initialized";
        fitEndKey = "shutdown";
    } else {
        console.error(`JobProgressDetails: Host type '${metrics.host_type}' not supported.`);
        return <></>;
    }

    let elapsedTime = "";
    let statusKey = status as keyof typeof validStatuses;
    if (fitStartKey in metrics) {
        const startDate = Date.parse(metrics[fitStartKey]);
        if (fitEndKey in metrics) {
            elapsedTime = getTimeString(Date.parse(metrics[fitEndKey]) - startDate);
        } else if (validStatuses[statusKey] === validStatuses.IN_PROGRESS) {
            // only estimate elapsed time if the job is in progress
            elapsedTime = getTimeString(Date.now() - startDate);
        }
    }

    let roundMetricsArray = [];
    if (metrics.rounds) {
        roundMetricsArray = Array(metrics.rounds.length);
        for (const [round, roundMetrics] of Object.entries(metrics.rounds)) {
            roundMetricsArray[parseInt(round) - 1] = roundMetrics;
        }
    }

    const metricsFileName =
        metrics.host_type === "server" ? "server-metrics.json" : `client-metrics-${clientIndex}.json`;
    let metricsFileURL = "";
    if (window.URL.createObjectURL) {
        // adding this check here to avoid overly complicated mocking in tests
        metricsFileURL = window.URL.createObjectURL(new Blob([JSON.stringify(metrics, null, 4)]));
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

            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Logs:</strong>
                </div>
                <div className="col-sm job-details-button">
                    <a className="btn btn-link show-logs-button" onClick={() => setShowLogs(true)}>
                        Show Logs
                    </a>
                </div>
            </div>
            <div className="row">
                <div className="col-sm-4 job-details-download-button">
                    <a
                        className="btn btn-link download-metrics-button"
                        title="Download metrics as JSON"
                        href={metricsFileURL}
                        download={metricsFileName}
                    >
                        <i className="material-icons">download</i>
                        Download Metrics as JSON
                    </a>
                </div>
            </div>

            {showLogs ? (
                <JobLogsModal
                    hostType={metrics.host_type}
                    jobId={jobId}
                    clientIndex={clientIndex}
                    setShowLogs={setShowLogs}
                />
            ) : null}
        </div>
    );
}

export function JobProgressRound({ roundMetrics, index }: { roundMetrics: RoundMetrics; index: number }): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    if (!roundMetrics) {
        return <></>;
    }

    return (
        <div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Round {index + 1}</strong>
                </div>
                <div className={`job-round-toggle-${index} col-sm job-details-button`}>
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

export function JobProgressRoundDetails({
    roundMetrics,
    index,
}: {
    roundMetrics: RoundMetrics;
    index: number;
}): ReactElement {
    if (!roundMetrics) {
        return <></>;
    }

    let fitStart = "";
    let fitEnd = "";
    if ("fit_start" in roundMetrics) {
        fitStart = roundMetrics.fit_start;
        fitEnd = roundMetrics.fit_end;
    }
    if ("fit_round_start" in roundMetrics) {
        fitStart = roundMetrics.fit_round_start;
        fitEnd = roundMetrics.fit_round_end;
    }

    let fitElapsedTime = "";
    if (fitStart) {
        const startDate = Date.parse(fitStart);
        const endDate = fitEnd ? Date.parse(fitEnd) : Date.now();
        fitElapsedTime = getTimeString(endDate - startDate);
    }

    let evalStart = null;
    let evalEnd = null;
    if ("eval_start" in roundMetrics) {
        evalStart = roundMetrics.eval_start;
        evalEnd = roundMetrics.eval_end;
    }
    if ("eval_round_start" in roundMetrics) {
        evalStart = roundMetrics.eval_round_start;
        evalEnd = roundMetrics.eval_round_end;
    }

    let evaluateElapsedTime = "";
    if (evalStart !== null) {
        const startDate = Date.parse(evalStart);
        const endDate = evalEnd ? Date.parse(evalEnd) : Date.now();
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
                <div className="col-sm">{fitStart}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Fit end time:</strong>
                </div>
                <div className="col-sm">{fitEnd}</div>
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
                <div className="col-sm">{evalStart}</div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Evaluate end time:</strong>
                </div>
                <div className="col-sm">{evalEnd}</div>
            </div>
            {Object.keys(roundMetrics).map((name, i) => (
                <JobProgressProperty name={name} value={roundMetrics[name]} key={i} />
            ))}
        </div>
    );
}

export function JobProgressProperty({ name, value }: { name: string; value: any }): ReactElement {
    const excludedProperties = [
        "fit_start",
        "fit_end",
        "fit_round_start",
        "fit_round_end",
        "eval_start",
        "eval_end",
        "eval_round_start",
        "eval_round_end",
        "rounds",
        "host_type",
        "initialized",
        "shutdown",
        "fit_elapsed_time",
        "fit_round_time_elapsed",
        "eval_round_time_elapsed",
    ];
    if (excludedProperties.includes(name)) {
        return <></>;
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

export function JobDetailsTable({
    Component,
    title,
    data,
    properties,
}: {
    Component: React.ComponentType<{ data: any; properties: JobDetailsProperties }>;
    title: string;
    data: any;
    properties: JobDetailsProperties;
}): ReactElement {
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

export function JobDetailsServerConfigTable({
    data,
    properties,
}: {
    data: string;
    properties: JobDetailsProperties;
}): ReactElement {
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
                                    {serverConfigJson[serverConfigName].toString()}
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
    properties: JobDetailsProperties;
}): ReactElement {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <table className="table align-items-center mb-0">
            <thead>
                <tr>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Address</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Data Path</th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Redis Address
                    </th>
                </tr>
            </thead>
            <tbody>
                {data.map((clientInfo, i) => {
                    let additionalClasses = clientInfo.metrics ? "" : "empty-cell";
                    return [
                        <tr className="job-client-details" key={`${i}-details`}>
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
                            <td className="col-sm" id={`job-details-client-config-redis-address-${i}`}>
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">{clientInfo.redis_address}</span>
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
                                colSpan={3}
                            >
                                <div className="d-flex flex-column justify-content-center">
                                    <span className="ps-3 text-secondary text-sm">
                                        <JobProgressBar
                                            metrics={clientInfo.metrics ?? ""}
                                            totalEpochs={properties.totalEpochs ?? 0}
                                            jobId={properties.jobId ?? "unknown"}
                                            jobStatus={properties.jobStatus ?? "NOT_STARTED"}
                                            clientIndex={i}
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

export function JobLogsModal({
    hostType,
    jobId,
    setShowLogs,
    clientIndex,
}: {
    hostType: string;
    jobId: string;
    setShowLogs: (showLogs: boolean) => void;
    clientIndex?: number;
}): ReactElement {
    let apiKey: string = "";
    let fileName: string = "";

    if (hostType === "server") {
        apiKey = getServerLogsKey(jobId);
        fileName = "server.log";
    } else if (hostType === "client") {
        apiKey = getClientLogsKey(jobId, clientIndex ?? -1);
        fileName = `client-${clientIndex}.log`;
    }

    const { data, error, isLoading, isValidating, mutate } = useSWRWithKey(apiKey);

    let dataURL = "";
    if (data) {
        dataURL = window.URL.createObjectURL(new Blob([data]));
    }

    return (
        <div className="log-viewer modal show" tabIndex={-1}>
            <div className="modal-dialog modal-dialog-scrollable">
                <div className="modal-content">
                    <div className="modal-header">
                        <h1 className="modal-title fs-5">Log Viewer</h1>
                        <a className="refresh-button" onClick={() => mutate(apiKey)}>
                            <i className="material-icons">refresh</i>
                        </a>
                        <a className="download-button" title="Download" href={dataURL} download={fileName}>
                            <i className="material-icons">download</i>
                        </a>
                        <button type="button" className="btn-close" onClick={() => setShowLogs(false)}>
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>

                    <div className="modal-body">
                        {isLoading || isValidating ? (
                            <div className="loading-container">
                                <Image src={loading_gif} alt="Loading Logs" height={64} width={64} />
                            </div>
                        ) : error ? (
                            "Error loading logs"
                        ) : (
                            data
                        )}
                    </div>
                </div>
            </div>
        </div>
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
