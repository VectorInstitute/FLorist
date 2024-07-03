"use client"

import { useSearchParams } from "next/navigation"
import Image from "next/image";

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

    return (
        <div className="container pt-3 p-0">
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Job ID:</strong>
                </div>
                <div className="col-sm" id="job-details-id">
                    {job._id}
                </div>
            </div>
            <div className="row">
                <div className="col-sm-2 align-content-center">
                    <strong className="text-dark">Status:</strong>
                </div>
                <div className="col-sm">
                    <JobDetailsStatus status={job.status} />
                </div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Model:</strong>
                </div>
                <div className="col-sm" id="job-details-model">
                    {job.model}
                </div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Server Address:</strong>
                </div>
                <div className="col-sm" id="job-details-server-address">
                    {job.server_address}
                </div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Redis Host:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-host">
                    {job.redis_host}
                </div>
            </div>
            <div className="row">
                <div className="col-sm-2">
                    <strong className="text-dark">Redis Port:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-port">
                    {job.redis_port}
                </div>
            </div>

            <h5 className="mb-0 pt-3">Server Configuration:</h5>
            <JobDetailsServerConfig serverConfig={job.server_config} />

            <h5 className="mb-0 pt-3">Clients Configuration:</h5>
            <JobDetailsClientsInfo clientsInfo={job.clients_info} />
        </div>
    );
}

export function JobDetailsStatus({ status }: { status: string }): ReactElement {
    let pillClasses = "status-pill ";
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
            <i className="material-icons text-sm" id="job-details-status-icon">{iconName}</i>&nbsp;
            {statusDescription}
        </div>
    );
}

export function JobDetailsServerConfig({ serverConfig }: { serverConfig: string }): ReactElement {
    const emptyResponse = (
        <div className="container pt-3 p-0" id="job-details-server-config-empty">
            Empty.
        </div>
    );

    if (!serverConfig) {
        return emptyResponse;
    }

    const serverConfigJson = JSON.parse(serverConfig);

    if (typeof serverConfigJson != "object" || Array.isArray(serverConfigJson)) {
        return (
            <div className="container pt-3 p-0" id="job-details-server-config-error">
                Error parsing server configuration.
            </div>
        );
    }

    const serverConfigNames = Object.keys(serverConfigJson);

    if (serverConfigNames.length === 0) {
        return emptyResponse;
    }

    return (
        <div className="container pt-3 p-0">
            {serverConfigNames.map((serverConfigName, i) => (
                <div className="row" key={i}>
                    <div className="col-sm-2" id={`job-details-server-config-name-${i}`}>
                        <strong className="text-dark">{serverConfigName}:</strong>
                    </div>
                    <div className="col-sm" id={`job-details-server-config-value-${i}`}>
                        {serverConfigJson[serverConfigName]}
                    </div>
                </div>
            ))}
        </div>
    );
}

export function JobDetailsClientsInfo({ clientsInfo }: { clientsInfo: Array<ClientInfo> }): ReactElement {
    return (
        <div className="container pt-3 p-0">
            <div className="row">
                <div className="col-sm"><strong className="text-dark">Client</strong></div>
                <div className="col-sm"><strong className="text-dark">Address</strong></div>
                <div className="col-sm"><strong className="text-dark">Data Path</strong></div>
                <div className="col-sm"><strong className="text-dark">Redis Host</strong></div>
                <div className="col-sm"><strong className="text-dark">Redis Port</strong></div>
            </div>
            {clientsInfo.map((clientInfo, i) => (
                <div className="row" key={i}>
                    <div className="col-sm" id={`job-details-client-config-client-${i}`}>
                        {clientInfo.client}
                    </div>
                    <div className="col-sm" id={`job-details-client-config-service-address-${i}`}>
                        {clientInfo.service_address}
                    </div>
                    <div className="col-sm" id={`job-details-client-config-data-path-${i}`}>
                        {clientInfo.data_path}
                    </div>
                    <div className="col-sm" id={`job-details-client-config-redis-host-${i}`}>
                        {clientInfo.redis_host}
                    </div>
                    <div className="col-sm" id={`job-details-client-config-redis-port-${i}`}>
                        {clientInfo.redis_port}
                    </div>
                </div>
            ))}
        </div>
    );
}
