import "@testing-library/jest-dom";
import { render, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "@jest/globals";

import { useGetJob } from "../../../../../app/jobs/hooks";
import { validStatuses, JobData } from "../../../../../app/jobs/definitions";
import JobDetails from "../../../../../app/jobs/details/page";

const testJobId = "test-job-id";

jest.mock("../../../../../app/jobs/hooks");
jest.mock("next/navigation", () => ({
    ...require("next-router-mock"),
    useSearchParams: () => new Map([["id", testJobId]]),
}));

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function setupGetJobMock(data: JobData, isLoading: boolean = false, error = null) {
    useGetJob.mockImplementation((jobId: string) => {
        return { data, error, isLoading };
    });
}

function makeTestJob(): JobData {
    return {
        _id: testJobId,
        status: "NOT_STARTED",
        model: "test-model",
        server_address: "test-server-address",
        redis_host: "test-redis-host",
        redis_port: "test-redis-port",
        server_config: JSON.stringify({
            test_attribute_1: "test-value-1",
            test_attribute_2: "test-value-2",
        }),
        clients_info: [
            {
                client: "test-client-1",
                service_address: "test-service-address-1",
                data_path: "test-data-path-1",
                redis_host: "test-redis-host-1",
                redis_port: "test-redis-port-1",
            },
            {
                client: "test-client-2",
                service_address: "test-service-address-2",
                data_path: "test-data-path-2",
                redis_host: "test-redis-host-2",
                redis_port: "test-redis-port-2",
            },
        ],
    };
}

describe("Job Details Page", () => {
    it("Renders correctly", () => {
        const testJob = makeTestJob();
        setupGetJobMock(testJob);
        const { container } = render(<JobDetails />);

        expect(useGetJob).toBeCalledWith(testJobId);

        expect(container.querySelector("h1")).toHaveTextContent("Job Details");
        expect(container.querySelector("#job-details-id")).toHaveTextContent(testJob._id);
        expect(container.querySelector("#job-details-status")).toHaveTextContent(validStatuses[testJob.status]);
        expect(container.querySelector("#job-details-status")).toHaveClass("status-pill");
        expect(container.querySelector("#job-details-server-address")).toHaveTextContent(testJob.server_address);
        expect(container.querySelector("#job-details-redis-host")).toHaveTextContent(testJob.redis_host);
        const testServerConfig = JSON.parse(testJob.server_config);
        const serverConfigNames = Object.keys(testServerConfig);
        for (let i = 0; i < serverConfigNames.length; i++) {
            expect(container.querySelector(`#job-details-server-config-name-${i}`)).toHaveTextContent(
                serverConfigNames[i],
            );
            expect(container.querySelector(`#job-details-server-config-value-${i}`)).toHaveTextContent(
                testServerConfig[serverConfigNames[i]],
            );
        }
        for (let i = 0; i < testJob.clients_info.length; i++) {
            expect(container.querySelector(`#job-details-client-config-client-${i}`)).toHaveTextContent(
                testJob.clients_info[i].client,
            );
            expect(container.querySelector(`#job-details-client-config-service-address-${i}`)).toHaveTextContent(
                testJob.clients_info[i].service_address,
            );
            expect(container.querySelector(`#job-details-client-config-data-path-${i}`)).toHaveTextContent(
                testJob.clients_info[i].data_path,
            );
            expect(container.querySelector(`#job-details-client-config-redis-host-${i}`)).toHaveTextContent(
                testJob.clients_info[i].redis_host,
            );
            expect(container.querySelector(`#job-details-client-config-redis-port-${i}`)).toHaveTextContent(
                testJob.clients_info[i].redis_port,
            );
        }
    });
    describe("Status", () => {
        it("Renders NOT_STARTED correctly", () => {
            const testJob = makeTestJob();
            testJob.status = "NOT_STARTED";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const statusComponent = container.querySelector("#job-details-status");
            expect(statusComponent).toHaveTextContent(validStatuses[testJob.status]);
            expect(statusComponent).toHaveClass("alert-info");
            const iconComponent = statusComponent.querySelector("#job-details-status-icon");
            expect(iconComponent).toHaveTextContent("radio_button_checked");
        });
        it("Renders IN_PROGRESS correctly", () => {
            const testJob = makeTestJob();
            testJob.status = "IN_PROGRESS";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const statusComponent = container.querySelector("#job-details-status");
            expect(statusComponent).toHaveTextContent(validStatuses[testJob.status]);
            expect(statusComponent).toHaveClass("alert-warning");
            const iconComponent = statusComponent.querySelector("#job-details-status-icon");
            expect(iconComponent).toHaveTextContent("sync");
        });
        it("Renders FINISHED_SUCCESSFULLY correctly", () => {
            const testJob = makeTestJob();
            testJob.status = "FINISHED_SUCCESSFULLY";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const statusComponent = container.querySelector("#job-details-status");
            expect(statusComponent).toHaveTextContent(validStatuses[testJob.status]);
            expect(statusComponent).toHaveClass("alert-success");
            const iconComponent = statusComponent.querySelector("#job-details-status-icon");
            expect(iconComponent).toHaveTextContent("check_circle");
        });
        it("Renders FINISHED_WITH_ERROR correctly", () => {
            const testJob = makeTestJob();
            testJob.status = "FINISHED_WITH_ERROR";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const statusComponent = container.querySelector("#job-details-status");
            expect(statusComponent).toHaveTextContent(validStatuses[testJob.status]);
            expect(statusComponent).toHaveClass("alert-danger");
            const iconComponent = statusComponent.querySelector("#job-details-status-icon");
            expect(iconComponent).toHaveTextContent("error");
        });
        it("Renders unknown status correctly", () => {
            const testJob = makeTestJob();
            testJob.status = "some inexistent status";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const statusComponent = container.querySelector("#job-details-status");
            expect(statusComponent).toHaveTextContent(testJob.status);
            expect(statusComponent).toHaveClass("alert-secondary");
            const iconComponent = statusComponent.querySelector("#job-details-status-icon");
            expect(iconComponent).toHaveTextContent("");
        });
    });
    describe("Server config", () => {
        it("Does not break when it's null", () => {
            const testJob = makeTestJob();
            testJob.server_config = null;
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const serverConfigComponent = container.querySelector("#job-details-server-config-empty");
            expect(serverConfigComponent).toHaveTextContent("Empty.");
        });
        it("Does not break when it's an empty dictionary", () => {
            const testJob = makeTestJob();
            testJob.server_config = JSON.stringify({});
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const serverConfigComponent = container.querySelector("#job-details-server-config-empty");
            expect(serverConfigComponent).toHaveTextContent("Empty.");
        });
        it("Does not break when it's not a dictionary", () => {
            const testJob = makeTestJob();
            testJob.server_config = JSON.stringify(["bad server config"]);
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const serverConfigComponent = container.querySelector("#job-details-server-config-error");
            expect(serverConfigComponent).toHaveTextContent("Error parsing server configuration.");
        });
    });
    it("Renders loading gif correctly", () => {
        setupGetJobMock(null, true);
        const { container } = render(<JobDetails />);
        const loadingComponent = container.querySelector("img#job-details-loading");
        expect(loadingComponent.getAttribute("alt")).toBe("Loading");
    });
    it("Renders error message when job is null", () => {
        setupGetJobMock(null);
        const { container } = render(<JobDetails />);
        expect(container.querySelector("#job-details-error")).toHaveTextContent("Error retrieving job.");
    });
    it("Renders error message when there is an error", () => {
        setupGetJobMock({}, false, "error");
        const { container } = render(<JobDetails />);
        expect(container.querySelector("#job-details-error")).toHaveTextContent("Error retrieving job.");
    });
});
