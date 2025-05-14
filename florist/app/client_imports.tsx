"use client";

import { useEffect } from "react";
import { getAuthHeaders } from "./auth";

function ClientImports(): null {
    useEffect(() => {
        require("./assets/js/core/popper.min.js");
        require("./assets/js/core/bootstrap.min.js");
        require("./assets/js/material-dashboard.js?v=3.1.0");
    }, []);

    return null;
}

const fetcher = (url: string) => {
    // Adding the authentication token to the request headers
    const params: RequestInit = {
        headers: new Headers(getAuthHeaders()),
    };

    return fetch(url, params).then((res) => {
        if (res.status === 401) {
            // redirecting to the login page in case any calls return a 401 (unauthorized) error
            window.location.href = "/login";
        }
        if (res.status != 200) {
            throw new Error(res.status.toString(), { cause: res.json() });
        }
        return res.json();
    });
};

export { fetcher };
export default ClientImports;
