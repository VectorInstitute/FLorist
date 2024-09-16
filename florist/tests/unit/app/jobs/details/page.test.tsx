import "@testing-library/jest-dom";
import { render, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "@jest/globals";
import { act } from "react-dom/test-utils";

import { useGetJob } from "../../../../../app/jobs/hooks";
import { validStatuses, JobData } from "../../../../../app/jobs/definitions";
import JobDetails from "../../../../../app/jobs/details/page";

const testJobId = "test-job-id";

jest.mock("../../../../../app/jobs/hooks");
jest.mock("next/navigation", () => ({
    ...require("next-router-mock"),
    useSearchParams: () => new Map([["id", testJobId]]),
}));
jest.useFakeTimers().setSystemTime(new Date("2020-01-01 12:12:12.1212"));

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
            n_server_rounds: 4,
        }),
        server_metrics: JSON.stringify({
            fit_start: "2020-01-01 12:07:07.0707",
            rounds: {
                "1": {fit_start: "2020-01-01 12:08:08.0808", fit_end: "2020-01-01 12:09:09.0909"},
                "2": {fit_start: "2020-01-01 12:10:10.1010", fit_end: "2020-01-01 12:11:11.1111"},
                "3": {fit_start: "2020-01-01 12:12:00.1212"},
            },
            custom_property_value: "133.7",
            custom_property_array: [1337, 1338],
            custom_property_object: {
                custom_property_object_value: "test",
            },
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
    describe("Job progress", () => {
        it("Does not display when there are no server metrics", () => {
            const testJob = makeTestJob();
            testJob.server_metrics = null;
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            expect(jobProgressComponent).toBeNull();
        });
        it("Display progress bar at 0% when there are no information about rounds", () => {
            const testJob = makeTestJob();
            testJob.server_metrics = JSON.stringify({});
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar.getAttribute("style")).toBe("width: 100%;");
            expect(progressBar).toHaveTextContent("0%");
            expect(progressBar).toHaveClass("bg-disabled");
        });
        it("Display progress bar at 0% when rounds list is empty", () => {
            const testJob = makeTestJob();
            testJob.server_metrics = JSON.stringify({rounds: {}});
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar.getAttribute("style")).toBe("width: 100%;");
            expect(progressBar).toHaveTextContent("0%");
            expect(progressBar).toHaveClass("bg-disabled");
        });
        it("Display progress bar at with correct progress percent", () => {
            setupGetJobMock(makeTestJob());
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar.getAttribute("style")).toBe("width: 50%;");
            expect(progressBar).toHaveTextContent("50%");
        });
        it("Display progress bar with correct class for NOT_STARTED status", () => {
            const testJob = makeTestJob();
            testJob.status = "NOT_STARTED";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar).toHaveClass("progress-bar-striped");
        });
        it("Display progress bar with correct class for IN_PROGRESS status", () => {
            const testJob = makeTestJob();
            testJob.status = "IN_PROGRESS";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar).toHaveClass("bg-warning");
        });
        it("Display progress bar with correct class for FINISHED_SUCCESSFULLY status", () => {
            const testJob = makeTestJob();
            testJob.status = "FINISHED_SUCCESSFULLY";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar).toHaveClass("bg-success");
        });
        it("Display progress bar with correct class for FINISHED_WITH_ERROR status", () => {
            const testJob = makeTestJob();
            testJob.status = "FINISHED_WITH_ERROR";
            setupGetJobMock(testJob);
            const { container } = render(<JobDetails />);
            const jobProgressComponent = container.querySelector("#job-progress");
            const progressBar = container.querySelector("div.progress-bar");
            expect(progressBar).toHaveClass("bg-danger");
        });
        describe("Details", () => {
            it("Should be collapsed by default", () => {
                setupGetJobMock(makeTestJob());
                const { container } = render(<JobDetails />);
                const jobProgressDetailsComponent = container.querySelector("#job-progress-detail");
                expect(jobProgressDetailsComponent).toBeNull();
            });
            it("Should open when the toggle button is clicked", () => {
                setupGetJobMock(makeTestJob());
                const { container } = render(<JobDetails />);
                const toggleButton = container.querySelector("#job-details-toggle a");
                expect(toggleButton).toHaveTextContent("Expand");

                act(() => toggleButton.click());

                const jobProgressDetailsComponent = container.querySelector("#job-progress-detail");
                expect(jobProgressDetailsComponent).not.toBeNull();
                expect(toggleButton).toHaveTextContent("Collapse");
            });
            it("Should render the contents correctly", () => {
                const testJob = makeTestJob();
                const serverMetrics = JSON.parse(testJob.server_metrics);
                setupGetJobMock(testJob);
                const { container } = render(<JobDetails />);
                const toggleButton = container.querySelector("#job-details-toggle a");
                act(() => toggleButton.click());

                const jobProgressDetailsComponent = container.querySelector("#job-progress-detail");
                const elapsedTime = jobProgressDetailsComponent.children[0];
                expect(elapsedTime.children[0]).toHaveTextContent("Elapsed time:");
                expect(elapsedTime.children[1]).toHaveTextContent("05m 05s");
                const fitStart = jobProgressDetailsComponent.children[1];
                expect(fitStart.children[0]).toHaveTextContent("Start time:");
                expect(fitStart.children[1]).toHaveTextContent(serverMetrics.fit_start);
                const fitEnd = jobProgressDetailsComponent.children[2];
                expect(fitEnd.children[0]).toHaveTextContent("End time:");
                expect(fitEnd.children[1]).toHaveTextContent("");

                // custom properties
                const customPropertyValue = jobProgressDetailsComponent.children[3];
                expect(customPropertyValue.children[0]).toHaveTextContent("custom_property_value");
                expect(customPropertyValue.children[1]).toHaveTextContent(serverMetrics.custom_property_value);
                const customPropertyArray = jobProgressDetailsComponent.children[4];
                expect(customPropertyArray.children[0]).toHaveTextContent("custom_property_array");
                expect(customPropertyArray.children[1]).toHaveTextContent(
                    JSON.stringify(serverMetrics.custom_property_array)
                );
                const customPropertyObject = jobProgressDetailsComponent.children[5];
                expect(customPropertyObject.children[0]).toHaveTextContent("custom_property_object");
                const customPropertyObjectValue = customPropertyObject.children[1];
                expect(customPropertyObjectValue.children[0].children[0]).toHaveTextContent("custom_property_object_value");
                expect(customPropertyObjectValue.children[0].children[1]).toHaveTextContent(
                    serverMetrics.custom_property_object.custom_property_object_value
                );

                // rounds
                const round1 = jobProgressDetailsComponent.children[6].children[0];
                expect(round1.children[0]).toHaveTextContent("Round 1");
                expect(round1.children[1].getAttribute("id")).toBe("job-round-toggle-0");
                const round2 = jobProgressDetailsComponent.children[7].children[0];
                expect(round2.children[0]).toHaveTextContent("Round 2");
                expect(round2.children[1].getAttribute("id")).toBe("job-round-toggle-1");
                const round3 = jobProgressDetailsComponent.children[8].children[0];
                expect(round3.children[0]).toHaveTextContent("Round 3");
                expect(round3.children[1].getAttribute("id")).toBe("job-round-toggle-2");
            });
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
