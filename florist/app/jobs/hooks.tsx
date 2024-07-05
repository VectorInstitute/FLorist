import { useState } from "react";
import useSWR, { mutate } from "swr";

import { fetcher } from "../client_imports";

export function useGetJobsByJobStatus(status: string) {
    const endpoint = `/api/server/job/status/${status}`;
    const { data, error, isLoading } = useSWR(endpoint, fetcher, {
        refresh_interval: 1000,
    });
    return { data, error, isLoading };
}

export function useGetJob(jobId: string) {
    return useSWR(`/api/server/job/${jobId}`, fetcher);
}

export function useGetModels() {
    return useSWR("/api/server/models", fetcher);
}

export function useGetClients() {
    return useSWR("/api/server/clients", fetcher);
}

export const usePost = () => {
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(null);
    const [response, setResponse] = useState(null);

    const post = async (path, body) => {
        setIsLoading(true);
        setResponse(null);
        setError(null);

        const response = await fetch(path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: body,
        });

        const json = await response.json();

        if (response.ok) {
            setResponse(json);
        } else {
            setError(json.error || true);
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};

export function refreshJobsByJobStatus(statuses: Array<string>) {
    statuses.forEach((status: string) => mutate(`/api/server/job/status/${status}`));
}
