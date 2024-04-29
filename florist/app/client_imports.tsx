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

const server_address_base = "http://localhost:8000/";
const fetcher = (...args) => fetch(...args).then(res => res.json());
const valid_statuses = {
    "NOT_STARTED": "Not Started",
    "IN_PROGRESS": "In Progress",
    "FINISHED_WITH_ERROR": "Finished with Error",
    "FINISHED_SUCCESSFULLY": "Finished Successfully"
};
export {server_address_base, fetcher, valid_statuses};
export default ClientImports;
