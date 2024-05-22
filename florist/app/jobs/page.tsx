"use client";

import { ReactElement } from "react/React";

import { useGetJobsByJobStatus } from "./hooks";

export const validStatuses = {
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

interface StatusProp {
    status: string;
}

export default function Page(): ReactElement {
    const statusComponents = Object.keys(validStatuses).map((key, i) => (
        <Status key={key} status={key} />
    ));
    return (
        <div className="mx-4">
            <h1> Job By Status </h1>
            {statusComponents}
        </div>
    );
}

export function Status({ status }: StatusProp): ReactElement {
    const { data, error, isLoading } = useGetJobsByJobStatus(status);
    if (error) return <span> Help1</span>;
    if (isLoading) return <span> Help2 </span>;

    return (
        <div>
            <h4 data-testid={`status-header-${status}`}>
                {validStatuses[status]}
            </h4>
            <StatusTable data={data} status={status} />
        </div>
    );
}

export function StatusTable({
    data,
    status,
}: {
    data: Array<JobData>;
    status: StatusProp;
}): ReactElement {
    if (data.length > 0) {
        return (
            <table data-testid={`status-table-${status}`} className="table">
                <thead>
                    <tr>
                        <th style={{ width: "25%" }}>Model</th>
                        <th style={{ width: "25%" }}>Server Address</th>
                        <th style={{ width: "50%" }}>
                            Client Service Addresses{" "}
                        </th>
                    </tr>
                </thead>
                <TableRows data={data} />
            </table>
        );
    } else {
        return (
            <div>
                <span data-testid={`status-no-jobs-${status}`}>
                    {" "}
                    No jobs to display.{" "}
                </span>
            </div>
        );
    }
}

export function TableRows({ data }: { data: Array<JobData> }): ReactElement {
    const tableRows = data.map((d, i) => (
        <TableRow
            key={i}
            model={d.model}
            serverAddress={d.server_address}
            clientsInfo={d.clients_info}
        />
    ));

    return <tbody>{tableRows}</tbody>;
}

export function TableRow({
    model,
    serverAddress,
    clientsInfo,
}: {
    model: string;
    serverAddress: string;
    clientsInfo: Array<ClientInfo>;
}): ReactElement {
    return (
        <tr>
            <td>{model}</td>
            <td>{serverAddress}</td>
            <ClientListTableData clientsInfo={clientsInfo} />
        </tr>
    );
}

export function ClientListTableData({
    clientsInfo,
}: {
    clientsInfo: Array<ClientInfo>;
}): ReactElement {
    const clientServiceAddressesString = clientsInfo
        .map((c) => c.service_address)
        .join(", ");
    return <td> {clientServiceAddressesString} </td>;
}
