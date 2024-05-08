"use client";

import { useEffect } from "react";

function ClientImports(): null {
    useEffect(() => {
        require("./assets/js/core/popper.min.js");
        require("./assets/js/core/bootstrap.min.js");
        require("./assets/js/material-dashboard.min.js?v=3.0.0");
    }, []);

    return null;
}

const fetcher = (...args) => fetch(...args).then((res) => res.json());
export { fetcher };
export default ClientImports;
