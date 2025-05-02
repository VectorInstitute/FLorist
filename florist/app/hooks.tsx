import { useState } from "react";
import { getAuthHeaders } from "./auth";

const DEFAULT_HEADERS: Array<[string, string]> = [["Content-Type", "application/json"]];

export const usePost = () => {
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [response, setResponse] = useState<any | null>(null);

    const post = async (
        path: string,
        body: string | FormData,
        headers: Array<[string, string]> | null = DEFAULT_HEADERS,
    ) => {
        setIsLoading(true);
        setResponse(null);
        setError(null);

        if (headers) {
            headers.push(...getAuthHeaders());
        }
        const requestHeaders = headers ? new Headers(headers) : undefined;

        const response = await fetch(path, { method: "POST", body: body, headers: requestHeaders });

        let json = await response.json();
        if (response.ok) {
            setResponse(json);
        } else {
            // Redirecting to the login page in case of a 401 (unauthorized) error
            if (json.status === 401) {
                window.location.href = "/login";
            }
            setError(json.error || json.detail || "An error occurred");
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};
