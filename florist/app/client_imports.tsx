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

const fetcher = (...args) => fetch(...args).then((res) => res.json());
const poster = params => url => post(url, params);
export { fetcher, poster };
export default ClientImports;
