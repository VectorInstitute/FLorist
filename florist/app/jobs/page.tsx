"use client"
import { ReactElement } from "react/React";
import useSWR from 'swr';
import ClientImports, {fetcher, server_address_base, valid_statuses} from '../client_imports';

export default function Page(): ReactElement {
    const status_components = Object.keys(valid_statuses).map(key => <Status status={key}/>);
    return (
        <div className="mx-4">
            <h1> Job Status </h1>
            {status_components}
        </div>
    );
}

function Status({ status }) : ReactElement {
    const endpoint = server_address_base.concat("api/server/job/").concat(status);
    const {data, error, isLoading} = useSWR(endpoint, fetcher, {refresh_interval: 1000});
    if (error) return <span> </span>
    if (isLoading) return <span> </span>

    return (
        <span>
            <h4> {valid_statuses[status]} </h4>
            <StatusTable
                data={data}
            />
        </span>
    );
}

function StatusTable( { data } ) : ReactElement {
    if (data.length > 0) {
        return (
           <table className="table">
                <tr>
                    <th style={{ width: '25%' }}>Model</th>
                    <th style={{ width: '25%' }}>Server Address</th>
                    <th style={{ width: '50%' }}>Client Service Addresses </th>
                </tr>
                <TableRows data={data} />
           </table>
        );
    }
}

function TableRows ( { data } ) : ReactElement {
    const table_rows = data.map(d =>
        <TableRow
            model={d.model}
            server_address={d.server_address}
            clients_info={d.clients_info}
        />
    );

    return table_rows;
}

function TableRow ( { model, server_address, clients_info } ) : ReactElement {
    return (
        <tr>
            <td>{model}</td>
            <td>{server_address}</td>
            <ClientListTableData clients_info={clients_info}/>
        </tr>
    );
}

function ClientListTableData ( { clients_info } ) : ReactElement {
    const client_service_addresses_string = clients_info.map(c => c.service_address).join(', ');
    return <td> {client_service_addresses_string} </td>
}
