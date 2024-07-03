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
                <Image src={loading_gif} alt="Loading" height={64} width={64} />
            </div>
        );
    }
    if (job) {
        return (
            <div className="container pt-3 p-0">
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Job ID:</strong>
                    </div>
                    <div className="col-sm">
                        {job._id}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Status:</strong>
                    </div>
                    <div className="col-sm">
                        {validStatuses[job.status]}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Model:</strong>
                    </div>
                    <div className="col-sm">
                        {job.model}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Server Address:</strong>
                    </div>
                    <div className="col-sm">
                        {job.server_address}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Redis Host:</strong>
                    </div>
                    <div className="col-sm">
                        {job.redis_host}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-2">
                        <strong className="text-dark">Redis Port:</strong>
                    </div>
                    <div className="col-sm">
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
    return null;
}

export function JobDetailsServerConfig({ serverConfig }: { serverConfig: string }): ReactElement {
    const serverConfigJson = JSON.parse(serverConfig);
    console.log(serverConfigJson)
    return (
        <div className="container pt-3 p-0">
            {serverConfigJson.map((serverConfigItem, i) => (
                <div className="row" key={i}>
                    <div className="col-sm-2">
                        <strong class="text-dark">{serverConfigItem.name}:</strong>
                    </div>
                    <div className="col-sm">
                        {serverConfigItem.value}
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
                    <div className="col-sm">{clientInfo.client}</div>
                    <div className="col-sm">{clientInfo.service_address}</div>
                    <div className="col-sm">{clientInfo.data_path}</div>
                    <div className="col-sm">{clientInfo.redis_host}</div>
                    <div className="col-sm">{clientInfo.redis_port}</div>
                </div>
            ))}
        </div>
    );
}
