import { useState } from "react";

const DEFAULT_HEADERS: Record<string, string> = { "Content-Type": "application/json" };

export const usePost = () => {
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [response, setResponse] = useState<any | null>(null);

    const post = async (path: string, body: any, headers: Record<string, string> = DEFAULT_HEADERS) => {
        setIsLoading(true);
        setResponse(null);
        setError(null);

        const response = await fetch(path, { method: "POST", body: body, headers: headers || undefined });

        let json = await response.json();
        if (response.ok) {
            setResponse(json);
        } else {
            setError(json.error || "An error occurred");
        }
        setIsLoading(false);
    };

    return { post, response, isLoading, error };
};
