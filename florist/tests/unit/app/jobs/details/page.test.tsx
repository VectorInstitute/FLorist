import "@testing-library/jest-dom";
import { getByText, render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "@jest/globals";

import { useGetJob } from "../../../../../app/jobs/hooks";
import { validStatuses, JobData } from "../../../../../app/jobs/definitions";
import JobDetails from "../../../../../app/jobs/details/page";

const testJobId = "test-job-id";

jest.mock("../../../../../app/jobs/hooks");
jest.mock('next/navigation', () => ({
    ...require("next-router-mock"),
    useSearchParams: () => new Map([["id", testJobId]]),
}));

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function setupMocks(jobData: JobData) {
    useGetJob.mockImplementation((jobId: string) => {
        return { data: jobData, error: null, isLoading: false };
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
            }, {
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
        setupMocks(testJob);
        const { container } = render(<JobDetails />);
        expect(container.querySelector("h1")).toHaveTextContent("Job Details");
        expect(container.querySelector("#job-details-id")).toHaveTextContent(testJob._id);
        expect(container.querySelector("#job-details-status")).toHaveTextContent(validStatuses[testJob.status]);
        expect(container.querySelector("#job-details-server-address")).toHaveTextContent(testJob.server_address);
        expect(container.querySelector("#job-details-redis-host")).toHaveTextContent(testJob.redis_host);
        const testServerConfig = JSON.parse(testJob.server_config);
        const serverConfigNames = Object.keys(testServerConfig);
        for (let i = 0; i < serverConfigNames.length; i++) {
            expect(container.querySelector(`#job-details-server-config-name-${i}`)).toHaveTextContent(
                serverConfigNames[i]
            );
            expect(container.querySelector(`#job-details-server-config-value-${i}`)).toHaveTextContent(
                testServerConfig[serverConfigNames[i]]
            );
        }
        for (let i = 0; i < testJob.clients_info.length; i++) {
            expect(container.querySelector(`#job-details-client-config-client-${i}`)).toHaveTextContent(
                testJob.clients_info[i].client
            );
            expect(container.querySelector(`#job-details-client-config-service-address-${i}`)).toHaveTextContent(
                testJob.clients_info[i].service_address
            );
            expect(container.querySelector(`#job-details-client-config-data-path-${i}`)).toHaveTextContent(
                testJob.clients_info[i].data_path
            );
            expect(container.querySelector(`#job-details-client-config-redis-host-${i}`)).toHaveTextContent(
                testJob.clients_info[i].redis_host
            );
            expect(container.querySelector(`#job-details-client-config-redis-port-${i}`)).toHaveTextContent(
                testJob.clients_info[i].redis_port
            );
        }
    });
});
