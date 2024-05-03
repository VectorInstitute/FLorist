import useSWR from "swr";
import { fetcher } from "../client_imports";

export default function useJobStatus(status: string) {
    const endpoint = "/api/server/job/".concat(status);
    const { data, error, isLoading } = useSWR(endpoint, fetcher, {
        refresh_interval: 1000,
    });
    return { data, error, isLoading };
}
