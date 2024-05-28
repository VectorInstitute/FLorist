import "@testing-library/jest-dom";
import { getByText, render, cleanup, fireEvent } from "@testing-library/react";
import { describe, afterEach, it, expect } from "@jest/globals";
import { act } from "react-dom/test-utils";

import EditJob, { makeEmptyJob } from "../../../../../app/jobs/edit/page";
import { useGetModels, useGetClients, usePost } from "../../../../../app/jobs/hooks";

jest.mock("../../../../../app/jobs/hooks");
jest.mock("next/navigation", () => ({
    useRouter() {
        return {
            prefetch: () => null
        };
    }
}));

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function setupGetMocks(modelsData, clientsData) {
    useGetModels.mockImplementation(() => {
        return {data: modelsData, error: null, isLoading: false};
    });
    useGetClients.mockImplementation(() => {
        return {data: clientsData, error: null, isLoading:false};
    });
}

function setupPostMocks(withError) {
    postMock = jest.fn();
    usePost.mockImplementation(() => {
        return {
            post: postMock,
            response: null,
            isLoading: null,
            error: withError,
        };
    });
    return postMock;
}

describe("New Job Page", () => {
    it("Renders correctly", () => {
        setupGetMocks();
        setupPostMocks();
        const { container } = render(<EditJob />);
        const h1 = container.querySelector("h1");
        expect(h1).toBeInTheDocument();
        expect(h1).toHaveTextContent("New Job");

        const successAlert = container.querySelector("div#job-saved-successfully");
        expect(successAlert).not.toBeInTheDocument();

        const errorAlert = container.querySelector("div#job-save-error");
        expect(errorAlert).not.toBeInTheDocument();
    });
    describe("Server Attributes", () => {
        it("Render Correctly", () => {
            const testModelsData = ["TEST-MODEL-1", "TEST-MODEL-2"];
            setupGetMocks(testModelsData, null);
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobModel = container.querySelector("select#job-model");
            expect(jobModel).toBeInTheDocument();
            const options = jobModel.querySelectorAll("option");
            expect(options.length).toBe(3);
            expect(options[0].value).toBe("empty");
            for (let i = 0; i < testModelsData.length; i++) {
                expect(options[i + 1].value).toBe(testModelsData[i]);
            }

            const jobServerAddress = container.querySelector("input#job-server-address");
            expect(jobServerAddress).toBeInTheDocument();
            expect(jobServerAddress.value).toBe("")

            const jobRedisHost = container.querySelector("input#job-redis-host");
            expect(jobRedisHost).toBeInTheDocument();
            expect(jobRedisHost.value).toBe("")

            const jobRedisPort = container.querySelector("input#job-redis-port");
            expect(jobRedisPort).toBeInTheDocument();
            expect(jobRedisPort.value).toBe("")
        });
    });

    describe("Server Config", () => {
        it("Render Correctly", () => {
            setupPostMocks();
            const { container } = render(<EditJob />);

            const jobServerConfig = container.querySelector("div#job-server-config");
            const header = jobServerConfig.querySelector("h6");
            expect(header).toBeInTheDocument();
            expect(header).toHaveTextContent("Server Configuration");
            const addButton = jobServerConfig.querySelector("i#job-server-config-add");
            expect(addButton).toBeInTheDocument();
            expect(addButton).toHaveTextContent("add");

            const jobServerConfigName = container.querySelector("input#job-server-config-name-0");
            expect(jobServerConfigName).toBeInTheDocument();
            expect(jobServerConfigName.value).toBe("");

            const jobServerConfigValue = container.querySelector("input#job-server-config-value-0");
            expect(jobServerConfigValue).toBeInTheDocument();
            expect(jobServerConfigValue.value).toBe("");
        });
        it("Add button click adds a new element", () => {
            setupPostMocks();
            const { container } = render(<EditJob />);

            const jobServerConfig = container.querySelector("div#job-server-config");
            const addButton = jobServerConfig.querySelector("i#job-server-config-add");

            act(() => addButton.click());

            const jobServerConfigName = container.querySelector("input#job-server-config-name-1");
            expect(jobServerConfigName).toBeInTheDocument();
            expect(jobServerConfigName.value).toBe("");

            const jobServerConfigValue = container.querySelector("input#job-server-config-value-1");
            expect(jobServerConfigValue).toBeInTheDocument();
            expect(jobServerConfigValue.value).toBe("");
        });
    });

    describe("Server Config", () => {
        it("Render Correctly", () => {
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            setupGetMocks(null, testClientsData);
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobClientsInfo = container.querySelector("div#job-clients-info");
            const header = jobClientsInfo.querySelector("h6");
            expect(header).toBeInTheDocument();
            expect(header).toHaveTextContent("Clients Configuration");
            const addButton = jobClientsInfo.querySelector("i#job-clients-info-add");
            expect(addButton).toBeInTheDocument();
            expect(addButton).toHaveTextContent("add");

            const jobClientInfoClient = container.querySelector("select#job-client-info-client-0");
            expect(jobClientInfoClient).toBeInTheDocument();
            const options = jobClientInfoClient.querySelectorAll("option");
            expect(options.length).toBe(3);
            expect(options[0].value).toBe("empty");
            for (let i = 0; i < testClientsData.length; i++) {
                expect(options[i + 1].value).toBe(testClientsData[i]);
            }

            const jobClientInfoServiceAddress = container.querySelector("input#job-client-info-service-address-0");
            expect(jobClientInfoServiceAddress).toBeInTheDocument();
            expect(jobClientInfoServiceAddress.value).toBe("");

            const jobClientInfoDataPath = container.querySelector("input#job-client-info-data-path-0");
            expect(jobClientInfoDataPath).toBeInTheDocument();
            expect(jobClientInfoDataPath.value).toBe("");

            const jobClientInfoRedisHost = container.querySelector("input#job-client-info-redis-host-0");
            expect(jobClientInfoRedisHost).toBeInTheDocument();
            expect(jobClientInfoRedisHost.value).toBe("");

            const jobClientInfoRedisPort = container.querySelector("input#job-client-info-redis-port-0");
            expect(jobClientInfoRedisPort).toBeInTheDocument();
            expect(jobClientInfoRedisPort.value).toBe("");
        });
        it("Add button click adds a new element", () => {
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            setupGetMocks(null, testClientsData);
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobClientsInfo = container.querySelector("div#job-clients-info");
            const addButton = jobClientsInfo.querySelector("i#job-clients-info-add");

            act(() => addButton.click());

            const jobClientInfoClient = container.querySelector("select#job-client-info-client-1");
            expect(jobClientInfoClient).toBeInTheDocument();
            const options = jobClientInfoClient.querySelectorAll("option");
            expect(options.length).toBe(3);
            expect(options[0].value).toBe("empty");
            for (let i = 0; i < testClientsData.length; i++) {
                expect(options[i + 1].value).toBe(testClientsData[i]);
            }

            const jobClientInfoServiceAddress = container.querySelector("input#job-client-info-service-address-1");
            expect(jobClientInfoServiceAddress).toBeInTheDocument();
            expect(jobClientInfoServiceAddress.value).toBe("");

            const jobClientInfoDataPath = container.querySelector("input#job-client-info-data-path-1");
            expect(jobClientInfoDataPath).toBeInTheDocument();
            expect(jobClientInfoDataPath.value).toBe("");

            const jobClientInfoRedisHost = container.querySelector("input#job-client-info-redis-host-1");
            expect(jobClientInfoRedisHost).toBeInTheDocument();
            expect(jobClientInfoRedisHost.value).toBe("");

            const jobClientInfoRedisPort = container.querySelector("input#job-client-info-redis-port-1");
            expect(jobClientInfoRedisPort).toBeInTheDocument();
            expect(jobClientInfoRedisPort.value).toBe("");
        });
    });

    describe("Form Submit", () => {
        it("Submits data correctly", async () => {
            const testModelsData = ["TEST-MODEL-1", "TEST-MODEL-2"];
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            setupGetMocks(testModelsData, testClientsData);
            postMock = setupPostMocks();

            const { container } = render(<EditJob />);

            const addServerConfigButton = container.querySelector("i#job-server-config-add");
            const addClientsInfoButton = container.querySelector("i#job-clients-info-add");
            act(() => addServerConfigButton.click());
            act(() => addClientsInfoButton.click());

            const testJob = {
                model: "TEST-MODEL-2",
                server_address: "test server address",
                redis_host: "test redis host",
                redis_port: "test redis port",
                server_config: [{
                    name: "test server config name 1",
                    value: "test server config value 1",
                }, {
                    name: "test server config name 2",
                    value: "test server config value 2",
                }],
                clients_info: [{
                    client: "TEST-CLIENT-1",
                    service_address: "test service address 1",
                    data_path: "test data path 1",
                    redis_host: "test redis host 1",
                    redis_port: "test redis port 1",
                }, {
                    client: "TEST-CLIENT-2",
                    service_address: "test service address 2",
                    data_path: "test data path 2",
                    redis_host: "test redis host 2",
                    redis_port: "test redis port 2",
                }],
            };

            const makeTargetValue = (value) => { return { "target": { "value": value }} };
            act(() => {
                fireEvent.change(container.querySelector("select#job-model"), makeTargetValue(testJob.model));
                fireEvent.change(container.querySelector("input#job-server-address"), makeTargetValue(testJob.server_address));
                fireEvent.change(container.querySelector("input#job-redis-host"), makeTargetValue(testJob.redis_host));
                fireEvent.change(container.querySelector("input#job-redis-port"), makeTargetValue(testJob.redis_port));
                fireEvent.change(container.querySelector("input#job-server-config-name-0"), makeTargetValue(testJob.server_config[0].name));
                fireEvent.change(container.querySelector("input#job-server-config-value-0"), makeTargetValue(testJob.server_config[0].value));
                fireEvent.change(container.querySelector("input#job-server-config-name-1"), makeTargetValue(testJob.server_config[1].name));
                fireEvent.change(container.querySelector("input#job-server-config-value-1"), makeTargetValue(testJob.server_config[1].value));
                fireEvent.change(container.querySelector("select#job-client-info-client-0"), makeTargetValue(testJob.clients_info[0].client));
                fireEvent.change(container.querySelector("input#job-client-info-service-address-0"), makeTargetValue(testJob.clients_info[0].service_address));
                fireEvent.change(container.querySelector("input#job-client-info-data-path-0"), makeTargetValue(testJob.clients_info[0].data_path));
                fireEvent.change(container.querySelector("input#job-client-info-redis-host-0"), makeTargetValue(testJob.clients_info[0].redis_host));
                fireEvent.change(container.querySelector("input#job-client-info-redis-port-0"), makeTargetValue(testJob.clients_info[0].redis_port));
                fireEvent.change(container.querySelector("select#job-client-info-client-1"), makeTargetValue(testJob.clients_info[1].client));
                fireEvent.change(container.querySelector("input#job-client-info-service-address-1"), makeTargetValue(testJob.clients_info[1].service_address));
                fireEvent.change(container.querySelector("input#job-client-info-data-path-1"), makeTargetValue(testJob.clients_info[1].data_path));
                fireEvent.change(container.querySelector("input#job-client-info-redis-host-1"), makeTargetValue(testJob.clients_info[1].redis_host));
                fireEvent.change(container.querySelector("input#job-client-info-redis-port-1"), makeTargetValue(testJob.clients_info[1].redis_port));
            });

            const submitButton = container.querySelector("button#job-post");
            await act(async () => await submitButton.click());

            testJob.server_config = JSON.stringify(testJob.server_config)
            expect(postMock).toBeCalledWith("/api/server/job", JSON.stringify(testJob));
        });

        it("Displays submit error", async () => {
            setupGetMocks();
            postMock = setupPostMocks(true);

            const { container } = render(<EditJob />);

            const submitButton = container.querySelector("button#job-post");
            await act(async () => await submitButton.click());

            const testJob = makeEmptyJob()
            testJob.server_config = JSON.stringify(testJob.server_config)
            expect(postMock).toBeCalledWith("/api/server/job", JSON.stringify(testJob));

            const errorAlert = container.querySelector("div#job-save-error");
            expect(errorAlert).toBeInTheDocument();
        });
    });
});
