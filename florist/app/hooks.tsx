import { useState } from "react";

import useSWR from "swr";
import Cookies from "js-cookie";

import { fetcher } from "./client_imports";

const DEFAULT_HEADERS: Record<string, string> = { "Content-Type": "application/json" };

export function getHeaders() {
    const componentType = typeof window === "undefined" ? "server" : "client";
    if (componentType == "server") {
        return {};
    }
    const token = Cookies.get("token");
    if (token) {
        return { headers: new Headers({ Authorization: `Bearer ${token}` }) };
    }
    return {};
}

export function useCheckToken() {
    return useSWR(["/api/server/auth/check_token", getHeaders()], fetcher);
}

export const usePost = () => {
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [response, setResponse] = useState<any | null>(null);

    const post = async (
        path: string,
        body: string | FormData,
        headers: Record<string, string> | null = DEFAULT_HEADERS,
    ) => {
        setIsLoading(true);
        setResponse(null);
        setError(null);

        const response = await fetch(path, { method: "POST", body: body, headers: headers || undefined });

        let json = await response.json();
        if (response.ok) {
            setResponse(json);
        } else {
            setError(json.error || json.detail || "An error occurred");
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};
