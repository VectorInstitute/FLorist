"use client";

import { useSearchParams } from "next/navigation";
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
            <div className="row pb-2 mb-4">
                <div className="col-sm-2">
                    <strong className="text-dark">Redis Port:</strong>
                </div>
                <div className="col-sm" id="job-details-redis-port">
                    {job.redis_port}
                </div>
            </div>

            <JobDetailsTableHeader
                Component={JobDetailsServerConfigTable}
                title="Server Configuration"
                data={job.server_config}
            />

            <JobDetailsTableHeader
                Component={JobDetailsClientsInfoTable}
                title="Clients Configuration"
                data={job.clients_info}
            />

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
            <i className="material-icons text-sm" id="job-details-status-icon">
                {iconName}
            </i>
            &nbsp;
            {statusDescription}
        </div>
    );
}

export function JobDetailsTableHeader({ Component, title, data }): ReactElement {
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
                            <Component data={data} />
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}

export function JobDetailsServerConfigTable({ data }: { data: string }): ReactElement {
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
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Name
                    </th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Value
                    </th>
                </tr>
            </thead>
            <tbody>
                {serverConfigNames.map((serverConfigName, i) => (
                    <tr key={i}>
                        <td className="col-sm-2" id={`job-details-server-config-name-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm font-weight-bold">
                                    {serverConfigName}
                                </span>
                            </div>
                        </td>
                        <td  className="col-sm" id={`job-details-server-config-value-${i}`}>
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

export function JobDetailsClientsInfoTable({ data }: { data: Array<ClientInfo> }): ReactElement {
    return (
        <table className="table align-items-center mb-0">
            <thead>
                <tr>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Client
                    </th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Address
                    </th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Data Path
                    </th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Redis Host
                    </th>
                    <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                        Redis Port
                    </th>
                </tr>
            </thead>
            <tbody>
                {data.map((clientInfo, i) => (
                    <tr key={i}>
                        <td  className="col-sm" id={`job-details-client-config-client-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {clientInfo.client}
                                </span>
                            </div>
                        </td>
                        <td  className="col-sm" id={`job-details-client-config-service-address-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {clientInfo.service_address}
                                </span>
                            </div>
                        </td>
                        <td  className="col-sm" id={`job-details-client-config-data-path-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {clientInfo.data_path}
                                </span>
                            </div>
                        </td>
                        <td  className="col-sm" id={`job-details-client-config-redis-host-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {clientInfo.redis_host}
                                </span>
                            </div>
                        </td>
                        <td  className="col-sm" id={`job-details-client-config-redis-port-${i}`}>
                            <div className="d-flex flex-column justify-content-center">
                                <span className="ps-3 text-secondary text-sm">
                                    {clientInfo.redis_port}
                                </span>
                            </div>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}
