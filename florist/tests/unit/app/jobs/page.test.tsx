import "@testing-library/jest-dom";
import { getByText, render, cleanup } from "@testing-library/react";
import { describe, afterEach, it, expect } from "@jest/globals";

import Page, { validStatuses } from "../../../../app/jobs/page";
import { useGetJobsByJobStatus } from "../../../../app/jobs/hooks";

jest.mock("../../../../app/jobs/hooks");

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function mockJobData(
    model: string,
    serverAddress: string,
    clientServicesAddresses: Array<string>,
) {
    const data = {
        model: model,
        server_address: serverAddress,
        clients_info: clientServicesAddresses.map((clientServicesAddress) => ({
            service_address: clientServicesAddress,
        })),
    };
    return data;
}

function setupMock(
    validStatuses: Array<string>,
    data: Array<object>,
    error: boolean,
    isLoading: boolean,
) {
    useGetJobsByJobStatus.mockImplementation((status: string) => {
        if (validStatuses.includes(status)) {
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
        expect(h1).toHaveTextContent("Jobs");
    });

    it("Renders Status Components Headers", () => {
        const data = [
            mockJobData("MNIST", "localhost:8080", ["localhost:7080"]),
        ];
        const validStatusesKeys = Object.keys(validStatuses);

        setupMock(validStatusesKeys, data, false, false);
        const { getByTestId } = render(<Page />);

        for (const status of validStatusesKeys) {
            const element = getByTestId(`status-header-${status}`);
            expect(element).toBeInTheDocument();
            expect(element).toHaveTextContent(validStatuses[status]);
        }
    });

    it("Renders Status Table With Table with Data", () => {
        const data = [
            mockJobData("MNIST", "localhost:8080", ["localhost:7080"]),
        ];
        const validStatusesKeys = Object.keys(validStatuses);

        setupMock(validStatusesKeys, data, false, false);

        const { getByTestId } = render(<Page />);

        for (const status of validStatusesKeys) {
            const element = getByTestId(`status-table-${status}`);
            expect(getByText(element, "Model")).toBeInTheDocument();
            expect(getByText(element, "Server Address")).toBeInTheDocument();
            expect(
                getByText(element, "Client Service Addresses"),
            ).toBeInTheDocument();
            expect(getByText(element, "MNIST")).toBeInTheDocument();
            expect(getByText(element, "localhost:8080")).toBeInTheDocument();
            expect(getByText(element, "localhost:7080")).toBeInTheDocument();
        }
    });

    it("Renders Status Table without Data", () => {
        setupMock([], [], false, false);
        const { getByTestId } = render(<Page />);

        for (const status of Object.keys(validStatuses)) {
            const element = getByTestId(`status-no-jobs-${status}`);
            expect(
                getByText(element, "No jobs to display."),
            ).toBeInTheDocument();
        }
    });
    it("Renders Loading GIF only when all isLoading", () => {
        setupMock(
            [
                "NOT_STARTED",
                "IN_PROGRESS",
                "FINISHED_SUCCESSFULLY",
                "FINISHED_WITH_ERROR",
            ],
            [],
            false,
            true,
        );
        const { getByTestId } = render(<Page />);
        const element = getByTestId("jobs-page-loading-gif");
        expect(element).toBeInTheDocument();
    });

    it("Doesn't Render Loading GIF when not Loading", () => {
        setupMock(
            [
                "NOT_STARTED",
                "IN_PROGRESS",
                "FINISHED_SUCCESSFULLY",
                "FINISHED_WITH_ERROR",
            ],
            [],
            false,
            false,
        );
        const { queryByTestId } = render(<Page />);
        const element = queryByTestId("jobs-page-loading-gif");
        expect(element).not.toBeInTheDocument();
    });
});
