"use client";

import { useEffect } from "react";

function ClientImports(): null {
    useEffect(() => {
        require("./assets/js/core/popper.min.js");
        require("./assets/js/core/bootstrap.min.js");
        require("./assets/js/material-dashboard.js?v=3.1.0");
    }, []);

    return null;
}

const fetcher = (...args: Parameters<typeof fetch>) =>
    fetch(...args).then((res) => {
        if (res.status != 200) {
            throw new Error(res.status.toString(), { cause: res.json() });
        }
        return res.json();
    });
export { fetcher };
export default ClientImports;
