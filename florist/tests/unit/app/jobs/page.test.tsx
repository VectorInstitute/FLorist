import "@testing-library/jest-dom";
import { getByText, render, cleanup } from "@testing-library/react";
import { describe, afterEach, it, expect } from "@jest/globals";

import Page from "../../../../app/jobs/page";
import useJobStatus from "../../../../app/jobs/hooks";

jest.mock("../../../../app/jobs/hooks");

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function mock_job_data(
    model: string,
    server_address: string,
    client_services_addresses: Array<string>,
) {
    const data = {
        model: model,
        server_address: server_address,
        clients_info: client_services_addresses.map(
            (client_services_address) => ({
                service_address: client_services_address,
            }),
        ),
    };
    return data;
}

function setupMock(
    valid_statuses: Array<string>,
    data: Array<object>,
    error: boolean,
    isLoading: boolean,
) {
    useJobStatus.mockImplementation((status: string) => {
        if (valid_statuses.includes(status)) {
            return {
                data,
                error,
                isLoading,
            };
        } else {
            return {
                data: [],
                error: false,
                isLoading: false,
            };
        }
    });
}

describe("List Jobs Page", () => {
    it("Renders Page Title correct", () => {
        setupMock([], [], false, false);
        const { container } = render(<Page />);
        const h1 = container.querySelector("h1");
        expect(h1).toBeInTheDocument();
        expect(h1).toHaveTextContent("Job Status");
    });

    it("Renders Status Components Headers", () => {
        const data = [
            mock_job_data("MNIST", "localhost:8080", ["localhost:7080"]),
        ];
        setupMock(
            [
                "NOT_STARTED",
                "IN_PROGRESS",
                "FINISHED_SUCCESSFULLY",
                "FINISHED_WITH_ERROR",
            ],
            data,
            false,
            false,
        );
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

    it("Renders Status Table With Table with Data", () => {
        const data = [
            mock_job_data("MNIST", "localhost:8080", ["localhost:7080"]),
        ];
        setupMock(
            [
                "NOT_STARTED",
                "IN_PROGRESS",
                "FINISHED_SUCCESSFULLY",
                "FINISHED_WITH_ERROR",
            ],
            data,
            false,
            false,
        );
        const { getByTestId } = render(<Page />);
        const ns_table = getByTestId("status-table-NOT_STARTED");

        expect(getByText(ns_table, "Model")).toBeInTheDocument();
        expect(getByText(ns_table, "Server Address")).toBeInTheDocument();
        expect(
            getByText(ns_table, "Client Service Addresses"),
        ).toBeInTheDocument();
        expect(getByText(ns_table, "MNIST")).toBeInTheDocument();
        expect(getByText(ns_table, "localhost:8080")).toBeInTheDocument();
        expect(getByText(ns_table, "localhost:7080")).toBeInTheDocument();

        const ip_table = getByTestId("status-table-IN_PROGRESS");

        expect(getByText(ip_table, "Model")).toBeInTheDocument();
        expect(getByText(ip_table, "Server Address")).toBeInTheDocument();
        expect(
            getByText(ip_table, "Client Service Addresses"),
        ).toBeInTheDocument();
        expect(getByText(ip_table, "MNIST")).toBeInTheDocument();
        expect(getByText(ip_table, "localhost:8080")).toBeInTheDocument();
        expect(getByText(ip_table, "localhost:7080")).toBeInTheDocument();

        const fs_table = getByTestId("status-table-FINISHED_SUCCESSFULLY");

        expect(getByText(fs_table, "Model")).toBeInTheDocument();
        expect(getByText(fs_table, "Server Address")).toBeInTheDocument();
        expect(
            getByText(fs_table, "Client Service Addresses"),
        ).toBeInTheDocument();
        expect(getByText(fs_table, "MNIST")).toBeInTheDocument();
        expect(getByText(fs_table, "localhost:8080")).toBeInTheDocument();
        expect(getByText(fs_table, "localhost:7080")).toBeInTheDocument();

        const fe_table = getByTestId("status-table-FINISHED_WITH_ERROR");

        expect(getByText(fe_table, "Model")).toBeInTheDocument();
        expect(getByText(fe_table, "Server Address")).toBeInTheDocument();
        expect(
            getByText(fe_table, "Client Service Addresses"),
        ).toBeInTheDocument();
        expect(getByText(fe_table, "MNIST")).toBeInTheDocument();
        expect(getByText(fe_table, "localhost:8080")).toBeInTheDocument();
        expect(getByText(fe_table, "localhost:7080")).toBeInTheDocument();
    });

    it("Renders Status Table With Table without Data", () => {
        setupMock([], [], false, false);
        const { getByTestId } = render(<Page />);

        const not_started = getByTestId("status-no-jobs-NOT_STARTED");
        expect(
            getByText(not_started, "No jobs to display."),
        ).toBeInTheDocument();

        const in_progress = getByTestId("status-no-jobs-IN_PROGRESS");
        expect(
            getByText(in_progress, "No jobs to display."),
        ).toBeInTheDocument();

        const finished_success = getByTestId(
            "status-no-jobs-FINISHED_SUCCESSFULLY",
        );
        expect(
            getByText(finished_success, "No jobs to display."),
        ).toBeInTheDocument();

        const finished_error = getByTestId(
            "status-no-jobs-FINISHED_WITH_ERROR",
        );
        expect(
            getByText(finished_error, "No jobs to display."),
        ).toBeInTheDocument();
    });
});
