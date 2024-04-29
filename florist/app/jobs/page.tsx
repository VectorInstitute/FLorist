"use client";
import { ReactElement } from "react/React";
import useSWR from "swr";
import { fetcher } from "../client_imports";

const valid_statuses = {
    NOT_STARTED: "Not Started",
    IN_PROGRESS: "In Progress",
    FINISHED_WITH_ERROR: "Finished with Error",
    FINISHED_SUCCESSFULLY: "Finished Successfully",
};

interface JobData {
    status: string;
    model: string;
    server_address: string;
    server_info: string;
    redis_host: string;
    redis_port: string;
    clients_info: Array<ClientInfo>;
}

interface ClientInfo {
    client: string;
    service_address: string;
    data_path: string;
    redis_host: string;
    redis_port: string;
}

export default function Page(): ReactElement {
    const status_components = Object.keys(valid_statuses).map((key) => (
        <Status key={key} status={key} />
    ));
    return (
        <div className="mx-4">
            <h1> Job Status </h1>
            {status_components}
        </div>
    );
}

function Status({ status }: { status: string }): ReactElement {
    const endpoint = "/api/server/job/".concat(status);
    const { data, error, isLoading } = useSWR(endpoint, fetcher, {
        refresh_interval: 1000,
    });
    if (error) return <span> </span>;
    if (isLoading) return <span> </span>;

    return (
        <span>
            <h4> {valid_statuses[status]} </h4>
            <StatusTable data={data} />
        </span>
    );
}

function StatusTable({ data }: { data: Array<JobData> }): ReactElement {
    if (data.length > 0) {
        return (
            <table className="table">
                <tr>
                    <th style={{ width: "25%" }}>Model</th>
                    <th style={{ width: "25%" }}>Server Address</th>
                    <th style={{ width: "50%" }}>Client Service Addresses </th>
                </tr>
                <TableRows data={data} />
            </table>
        );
    } else {
        return (
            <div>
                <span> No jobs to display. </span>
            </div>
        );
    }
}

function TableRows({ data }: { data: Array<JobData> }): ReactElement {
    const table_rows = data.map((d, i) => (
        <TableRow
            key={i}
            model={d.model}
            server_address={d.server_address}
            clients_info={d.clients_info}
        />
    ));

    return table_rows;
}

function TableRow({
    model,
    server_address,
    clients_info,
}: {
    model: string;
    server_address: string;
    clients_info: Array<ClientInfo>;
}): ReactElement {
    return (
        <tr>
            <td>{model}</td>
            <td>{server_address}</td>
            <ClientListTableData clients_info={clients_info} />
        </tr>
    );
}

function ClientListTableData({
    clients_info,
}: {
    clients_info: Array<ClientInfo>;
}): ReactElement {
    const client_service_addresses_string = clients_info
        .map((c) => c.service_address)
        .join(", ");
    return <td> {client_service_addresses_string} </td>;
}
