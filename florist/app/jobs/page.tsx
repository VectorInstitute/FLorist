"use client"
import { ReactElement } from "react/React";
import useSWR from 'swr';
import ClientImports, {fetcher, server_address_base, valid_statuses} from '../client_imports';

export default function Page(): ReactElement {
    const status_components = Object.keys(valid_statuses).map(key => <Status status={key}/>); 
    return (
        <div class="mx-4">
            <h1> Job Status </h1>
            {status_components}
        </div>
    );
}

function Status({ status }) : ReactElement {
    const endpoint = server_address_base.concat("api/server/job/").concat(status);
    const {data, error, isLoading} = useSWR(endpoint, fetcher);
    if (error) return <div> Error </div>
    if (isLoading) return <div> isLoading </div>


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
           <table class="table"> 
                <tr>
                    <th>Model</th>
                    <th>Server Address</th>
                    <th>Redis Host</th>
                    <th>Redis Port</th>
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
            redis_host={d.redis_host}
            redis_port={d.redis_port}
        />
    );

    return table_rows;
}

function TableRow ( { model, server_address, redis_host, redis_port } ) : ReactElement {
    return (
        <tr>
            <td>{model}</td>
            <td>{server_address}</td>
            <td>{redis_host}</td>
            <td>{redis_port}</td>
        </tr>
    );
}
