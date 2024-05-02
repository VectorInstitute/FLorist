import useSWR from "swr";
import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import { describe, beforeEach, it, expect } from "@jest/globals";

import Page from "../../../../app/jobs/page";

function mock_swr_fetch_data(
    status: string,
    model: string,
    service_address: string,
    client_services_addresses: Array<string>,
) {
    const data = {
        status: status,
        model: model,
        service_address: service_address,
        clients_info: client_services_addresses.map(
            (client_services_address) => ({
                service_address: client_services_address,
            }),
        ),
    };
    return [data];
}

jest.mock("swr", () => ({
    __esModule: true,
    default: jest.fn(),
}));

const mock_data = mock_swr_fetch_data(
    "NOT_STARTED",
    "MNIST",
    "localhost:8080",
    ["localhost:8081"],
);
beforeEach(() => {
    useSWR.mockImplementation(() => ({
        data: mock_data,
        error: null,
        isLoading: false,
    }));
});

describe("List Jobs Page", () => {
    it("Renders Page Title correct", () => {
        const { container } = render(<Page />);
        const h1 = container.querySelector("h1");
        expect(h1).toBeInTheDocument();
        expect(h1).toHaveTextContent("Job Status");
    });

    it("Renders Status Components Headers", () => {
        const { getByTestId } = render(<Page />);
        const ns_status = getByTestId("status-header-NOT_STARTED");
        const ip_status = getByTestId("status-header-IN_PROGRESS");
        const fs_status = getByTestId("status-header-FINISHED_SUCCESSFULLY");
        const fe_status = getByTestId("status-header-FINISHED_WITH_ERROR");
        expect(ns_status).toBeInTheDocument();
        expect(ns_status).toHaveTextContent("Not Started");
        expect(ip_status).toBeInTheDocument();
        expect(ip_status).toHaveTextContent("In Progress");
        expect(fs_status).toBeInTheDocument();
        expect(fs_status).toHaveTextContent("Finished Successfully");
        expect(fe_status).toBeInTheDocument();
        expect(fe_status).toHaveTextContent("Finished with Error");
    });
});
