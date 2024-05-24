import useSWR from "swr";
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
