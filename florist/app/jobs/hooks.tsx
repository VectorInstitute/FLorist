import { useState } from "react";
import useSWR, { mutate } from "swr";

import { fetcher } from "../client_imports";

export function useGetJobsByJobStatus(status: string) {
    const endpoint = `/api/server/job/status/${status}`;
    const { data, error, isLoading } = useSWR(endpoint, fetcher, {
        refreshInterval: 1000,
    });
    return { data, error, isLoading };
}

export function useGetJob(jobId: string | null) {
    return useSWR(jobId ? `/api/server/job/${jobId}` : null, fetcher);
}

export function useGetModels() {
    return useSWR("/api/server/models", fetcher);
}

export function useGetStrategies() {
    return useSWR("/api/server/strategies", fetcher);
}

export function useGetOptimizers() {
    return useSWR("/api/server/optimizers", fetcher);
}

export function useGetClients({ strategy }: { strategy: string }) {
    return useSWR(strategy ? `/api/server/clients/${strategy}` : null, fetcher);
}

export function getServerLogsKey(jobId: string) {
    return `/api/server/job/get_server_log/${jobId}`;
}

export function getClientLogsKey(jobId: string, clientIndex: number) {
    return `/api/server/job/get_client_log/${jobId}/${clientIndex}`;
}

export function useSWRWithKey(key: string) {
    return useSWR(key, fetcher);
}

export const usePost = () => {
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [response, setResponse] = useState<any | null>(null);

    const post = async (path: string, body: any) => {
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
            setError(json.error || "An error occurred");
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};

export function refreshJobsByJobStatus(statuses: Array<string>) {
    statuses.forEach((status: string) => mutate(`/api/server/job/status/${status}`));
}
