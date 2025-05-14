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

        var requestHeaders = undefined;
        if (headers) {
            requestHeaders = new Headers(headers.concat(getAuthHeaders()));
        }

        const response = await fetch(path, { method: "POST", body: body, headers: requestHeaders });

        const responseText = await response.text();
        let parsedResponse;
        try {
            parsedResponse = JSON.parse(responseText);
        } catch (error) {
            parsedResponse = responseText;
        }

        if (response.ok) {
            setResponse(parsedResponse);
        } else {
            // Redirecting to the login page in case of a 401 (unauthorized) error
            // (except on the login page itself)
            if (response.status === 401 && !window.location.href.includes("/login")) {
                window.location.href = "/login";
            }
            setError(parsedResponse.error || parsedResponse.detail || "An error occurred");
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};
