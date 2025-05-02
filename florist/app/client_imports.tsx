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
    // Adding the asuthentication token to the request headers if this is being run in a client context
    const params: RequestInit = {
        headers: new Headers(getAuthHeaders()),
    };

    return fetch(url, params).then((res) => {
        if (res.status === 401) {
            // redirecting to the login page in case any calls return a 401 error
            window.location.href = "/login";
        }
        if (res.status != 200) {
            throw new Error(res.status.toString(), { cause: res.json() });
        }
        return res.json();
    });
}

export { fetcher };
export default ClientImports;
