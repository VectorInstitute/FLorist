import { useState } from "react";
import useSWR, { mutate } from "swr";

import { fetcher } from "../client_imports";

export function useGetJobsByJobStatus(status: string) {
    const endpoint = "/api/server/job/".concat(status);
    const { data, error, isLoading } = useSWR(endpoint, fetcher, {
        refresh_interval: 1000,
    });
    return { data, error, isLoading };
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

export function refreshJobsByJobStatus() {
    mutate("/api/server/job/NOT_STARTED");
    mutate("/api/server/job/IN_PROGRESS");
    mutate("/api/server/job/FINISHED_SUCCESSFULLY");
    mutate("/api/server/job/FINISHED_WITH_ERROR");
}
