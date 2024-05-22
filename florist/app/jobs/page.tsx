"use client";
import { ReactElement } from "react/React";
import useGetJobsByStatus from "./hooks";
import useGetJobsByJobStatus from "./hooks";

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
        <div className="container-fluid py-4">
            {statusComponents}
        </div>
    );
}

export function Status({ status }: StatusProp): ReactElement {
    const { data, error, isLoading } = useGetJobsByJobStatus(status);
    if (error) return <span> Help1</span>;
    if (isLoading) return <span> Help2 </span>;

    return (
        <div className="row">
        <div className="col-12">
        <div className="card my-4">
            <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2">
            <div className="bg-gradient-primary shadow-primary border-radius-lg pt-4 pb-3">
            <h6 data-testid={`status-header-${status}`} className="text-white text-capitalize ps-3"> 
                {validStatuses[status]}
            </h6>
            </div>
            </div>
            <StatusTable data={data} status={status} />
        </div>
        </div>
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
            <div className="card-body px-0 pb-2">
            <div className="table-responsive p-0">
            <table data-testid={`status-table-${status}`} className="table align-items-center mb-0">
                <thead>
                    <tr>
                        <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Model</th>
                        <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Server Address</th>
                        <th className="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">
                            Client Service Addresses{" "}
                        </th>
                    </tr>
                </thead>
                <TableRows data={data} />
            </table>
            </div>
            </div>
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
            <td>
                <div className="d-flex flex-column justify-content-center">
                    <span className="ps-3 text-secondary text-xs font-weight-bold">{model}</span>
                </div>
            </td>
            <td>
                <div className="d-flex flex-column justify-content-center">
                    <span className="ps-3 text-secondary text-xs font-weight-bold">{serverAddress}</span>
                </div>
            </td>
            <td>
                <div className="d-flex flex-column justify-content-center">
                    <span className="ps-3 text-secondary text-xs font-weight-bold">               
                        <ClientListTableData clientsInfo={clientsInfo} />
                    </span>
                </div>
            </td>
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
    return <div> {clientServiceAddressesString} </div>;
}
