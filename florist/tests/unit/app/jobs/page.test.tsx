import "@testing-library/jest-dom";
import { getByText, render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect } from "@jest/globals";

import Page, { validStatuses } from "../../../../app/jobs/page";
import { useGetJobsByJobStatus, usePost } from "../../../../app/jobs/hooks";

jest.mock("../../../../app/jobs/hooks");

function mockJobData(model: string, serverAddress: string, clientServicesAddresses: Array<string>) {
    const data = {
        model: model,
        server_address: serverAddress,
        clients_info: clientServicesAddresses.map((clientServicesAddress) => ({
            service_address: clientServicesAddress,
        })),
    };
    return data;
}

function mockUseGetJobsByJobStatus(
    status: string,
    validStatuses: Array<string>,
    data: Array<object>,
    error: boolean,
    isLoading: boolean,
) {
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
}

function mockUsePost() {
    return {
        post: jest.fn(),
        response: null,
        isLoading: false,
        error: null,
    };
}

function setupMock(validStatuses: Array<string>, data: Array<object>, error: boolean, isLoading: boolean) {
    useGetJobsByJobStatus.mockImplementation((status: string) =>
        mockUseGetJobsByJobStatus(status, validStatuses, data, error, isLoading),
    );
    usePost.mockImplementation(() => mockUsePost());
}

// Function that mocks useGetJobsByJobStatus with different values on successive calls
// In particular, return data in the initial call and than no data in the subsequent call
// Grouped in fours because function is called once per status and 4 statuses exist
function setupChangingMock(validStatuses: Array<string>, data: Array<object>, error: boolean, isLoading: boolean) {
    useGetJobsByJobStatus
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, data, error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, data, error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, data, error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, data, error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, [], error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, [], error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, [], error, isLoading),
        )
        .mockImplementationOnce((status: string) =>
            mockUseGetJobsByJobStatus(status, validStatuses, [], error, isLoading),
        );

    usePost.mockImplementation(() => mockUsePost());
}

describe("List Jobs Page", () => {
    it("Renders Page Header Correctly", () => {
        setupMock([], [], false, false);
        const { container } = render(<Page />);
        const h1 = container.querySelector("h1");
        expect(h1).toBeInTheDocument();
        expect(h1).toHaveTextContent("Jobs");
        const newJobButton = container.querySelector("#new-job-button");
        expect(newJobButton).toBeInTheDocument();
        expect(newJobButton.href.endsWith("/jobs/edit")).toBeTruthy();
    });

    it("Renders Status Components Headers", () => {
        const data = [mockJobData("MNIST", "localhost:8080", ["localhost:7080"])];
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
        const data = [mockJobData("MNIST", "localhost:8080", ["localhost:7080"])];
        const validStatusesKeys = Object.keys(validStatuses);

        setupMock(validStatusesKeys, data, false, false);

        const { getByTestId } = render(<Page />);

        for (const status of validStatusesKeys) {
            const element = getByTestId(`status-table-${status}`);
            expect(getByText(element, "Model")).toBeInTheDocument();
            expect(getByText(element, "Server Address")).toBeInTheDocument();
            expect(getByText(element, "Client Service Addresses")).toBeInTheDocument();
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
            expect(getByText(element, "No jobs to display.")).toBeInTheDocument();
        }
    });
    it("Renders Loading GIF only when all isLoading", () => {
        setupMock(["NOT_STARTED", "IN_PROGRESS", "FINISHED_SUCCESSFULLY", "FINISHED_WITH_ERROR"], [], false, true);
        const { getByTestId } = render(<Page />);
        const element = getByTestId("jobs-page-loading-gif");
        expect(element).toBeInTheDocument();
    });

    it("Doesn't Render Loading GIF when not Loading", () => {
        setupMock(["NOT_STARTED", "IN_PROGRESS", "FINISHED_SUCCESSFULLY", "FINISHED_WITH_ERROR"], [], false, false);
        const { queryByTestId } = render(<Page />);
        const element = queryByTestId("jobs-page-loading-gif");
        expect(element).not.toBeInTheDocument();
    });

    it("Start training button present in NOT_STARTED jobs", () => {
        const data = [mockJobData("MNIST", "localhost:8080", ["localhost:7080"])];
        const validStatusesKeys = Object.keys(validStatuses);

        setupMock(validStatusesKeys, data, false, false);
        const { queryByTestId } = render(<Page />);
        const element = queryByTestId("start-training-button-0");
        expect(element).toBeInTheDocument();
    });

    it("Start training button not present without NOT_STARTED jobs", () => {
        const data = [mockJobData("MNIST", "localhost:8080", ["localhost:7080"])];
        const statuses = ["IN_PROGRESS"];

        setupMock(statuses, data, false, false);
        const { queryByTestId } = render(<Page />);
        const element = queryByTestId("start-training-button-0");
        expect(element).not.toBeInTheDocument();
    });

    it("Start training button not present after started", () => {
        const data = [mockJobData("MNIST", "localhost:8080", ["localhost:7080"])];
        const statuses = ["NOT_STARTED"];

        setupChangingMock(statuses, data, false, false);
        render(<Page />);
        const element = screen.queryByTestId("start-training-button-0");
        expect(element).toBeInTheDocument();

        const button = screen.getByRole("button", { name: /start/i });
        fireEvent.click(button);

        waitFor(() => {
            const new_element = screen.queryByTestId("start-training-button-0");
            expect(new_element).not.toBeInTheDocument();
        });
    });
});
