import "@testing-library/jest-dom";
import { render, cleanup, fireEvent } from "@testing-library/react";
import { describe, afterEach, it, expect } from "@jest/globals";
import { act } from "react-dom/test-utils";

import yaml from "js-yaml";
import { createHash } from "crypto";
import EditJob, { makeEmptyJob } from "../../../../../app/(root)/jobs/edit/page";
import {
    useGetModels,
    useGetClients,
    useGetStrategies,
    useGetOptimizers,
    usePost,
} from "../../../../../app/(root)/jobs/hooks";

jest.mock("../../../../../app/(root)/jobs/hooks");
jest.mock("next/navigation", () => ({
    useRouter() {
        return {
            prefetch: () => null,
        };
    },
}));

afterEach(() => {
    jest.clearAllMocks();
    cleanup();
});

function setupGetMocks(modelsData, clientsData, strategiesData, optimizersData) {
    useGetModels.mockImplementation(() => {
        return { data: modelsData, error: null, isLoading: false };
    });
    useGetClients.mockImplementation((strategy) => {
        return { data: clientsData, error: null, isLoading: false };
    });
    useGetStrategies.mockImplementation(() => {
        return { data: strategiesData, error: null, isLoading: false };
    });
    useGetOptimizers.mockImplementation(() => {
        return { data: optimizersData, error: null, isLoading: false };
    });
}

function setupPostMocks({ error, isLoading, response } = {}) {
    const post = jest.fn();
    usePost.mockImplementation(() => {
        return { post, response, isLoading, error };
    });
    return post;
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
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            const testOptimizersData = ["TEST-OPTIMIZER-1", "TEST-OPTIMIZER-2"];
            const testStrategiesData = ["TEST-STRATEGY-1", "TEST-STRATEGY-2"];
            setupGetMocks(testModelsData, testClientsData, testStrategiesData, testOptimizersData);
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobModel = container.querySelector("select#job-model");
            expect(jobModel).toBeInTheDocument();
            const jobModelOptions = jobModel.querySelectorAll("option");
            expect(jobModelOptions.length).toBe(3);
            expect(jobModelOptions[0].value).toBe("");
            expect(jobModelOptions[0].selected).toBe(true);
            expect(jobModelOptions[0].disabled).toBe(true);
            for (let i = 0; i < testModelsData.length; i++) {
                expect(jobModelOptions[i + 1].value).toBe(testModelsData[i]);
            }
            expect(useGetModels).toBeCalled();

            const jobClient = container.querySelector("select#job-client");
            expect(jobClient).toBeInTheDocument();
            const jobClientOptions = jobClient.querySelectorAll("option");
            expect(jobClientOptions.length).toBe(3);
            expect(jobClientOptions[0].value).toBe("");
            expect(jobClientOptions[0].selected).toBe(true);
            expect(jobClientOptions[0].disabled).toBe(true);
            for (let i = 0; i < testModelsData.length; i++) {
                expect(jobClientOptions[i + 1].value).toBe(testClientsData[i]);
            }
            expect(useGetClients).toBeCalledWith({ strategy: "" });

            const jobStrategy = container.querySelector("select#job-strategy");
            expect(jobStrategy).toBeInTheDocument();
            const jobStrategyOptions = jobStrategy.querySelectorAll("option");
            expect(jobStrategyOptions.length).toBe(3);
            expect(jobStrategyOptions[0].value).toBe("");
            expect(jobStrategyOptions[0].selected).toBe(true);
            expect(jobStrategyOptions[0].disabled).toBe(true);
            for (let i = 0; i < testStrategiesData.length; i++) {
                expect(jobStrategyOptions[i + 1].value).toBe(testStrategiesData[i]);
            }
            expect(useGetStrategies).toBeCalled();

            const jobOptimizer = container.querySelector("select#job-optimizer");
            expect(jobOptimizer).toBeInTheDocument();
            const jobOptimizerOptions = jobOptimizer.querySelectorAll("option");
            expect(jobOptimizerOptions.length).toBe(3);
            expect(jobOptimizerOptions[0].value).toBe("");
            expect(jobOptimizerOptions[0].selected).toBe(true);
            expect(jobOptimizerOptions[0].disabled).toBe(true);
            for (let i = 0; i < testOptimizersData.length; i++) {
                expect(jobOptimizerOptions[i + 1].value).toBe(testOptimizersData[i]);
            }
            expect(useGetOptimizers).toBeCalled();

            const jobServerAddress = container.querySelector("input#job-server-address");
            expect(jobServerAddress).toBeInTheDocument();
            expect(jobServerAddress.value).toBe("");

            const jobRedisAddress = container.querySelector("input#job-redis-address");
            expect(jobRedisAddress).toBeInTheDocument();
            expect(jobRedisAddress.value).toBe("");
        });
    });

    describe("Client select", () => {
        it("Fetches clients based on the selected strategy", () => {
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            const testStrategiesData = ["TEST-STRATEGY-1", "TEST-STRATEGY-2"];
            setupGetMocks(null, testClientsData, testStrategiesData, null);
            setupPostMocks();

            const { container } = render(<EditJob />);

            fireEvent.change(container.querySelector("select#job-strategy"), {
                target: { value: testStrategiesData[1] },
            });

            expect(useGetClients).toBeCalledWith({ strategy: testStrategiesData[1] });
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
        it("Remove button click removed the clicked element", () => {
            setupPostMocks();
            const { container } = render(<EditJob />);

            const jobServerConfig = container.querySelector("div#job-server-config");
            const removeButton = jobServerConfig.querySelector("i#job-server-config-remove-0");

            act(() => removeButton.click());

            const jobServerConfigName = container.querySelector("input#job-server-config-name-0");
            expect(jobServerConfigName).not.toBeInTheDocument();
            const jobServerConfigValue = container.querySelector("input#job-server-config-value-0");
            expect(jobServerConfigValue).not.toBeInTheDocument();
        });
        describe("Import Button", () => {
            it("renders correctly", () => {
                setupGetMocks();
                setupPostMocks();
                const { container } = render(<EditJob />);

                const jobServerConfig = container.querySelector("div#job-server-config");
                const importButton = jobServerConfig.querySelector("#job-server-config-import");
                expect(importButton).toHaveTextContent("Import JSON or YAML");

                const uploadFileButton = jobServerConfig.querySelector("#job-server-config-uploader");
                uploadFileButton.click = jest.fn();

                act(() => importButton.click());

                expect(uploadFileButton.click).toHaveBeenCalled();
            });
            const testData = [
                { name: "test_name_1", value: "test_value_1" },
                { name: "test_name_2", value: "test_value_2" },
                { name: "test_name_3", value: "test_value_3" },
            ];
            const testCases = [
                { name: ".yaml", fileName: "test.yaml", dumpFunction: yaml.dump },
                { name: ".yml", fileName: "test.yml", dumpFunction: yaml.dump },
                { name: ".json", fileName: "test.json", dumpFunction: JSON.stringify },
            ];
            for (let testCase of testCases) {
                it(`processes uploaded ${testCase.name} file correctly`, async () => {
                    setupGetMocks();
                    setupPostMocks();
                    const { container } = render(<EditJob />);

                    const jobServerConfig = container.querySelector("div#job-server-config");
                    const uploadFileButton = jobServerConfig.querySelector("#job-server-config-uploader");

                    const transformedTestData = Object.fromEntries(testData.map((d) => [d.name, d.value]));
                    const fileMock = {
                        name: testCase.fileName,
                        text: async () => testCase.dumpFunction(transformedTestData),
                    };

                    await act(async () => fireEvent.change(uploadFileButton, { target: { files: [fileMock] } }));

                    for (let i in testData) {
                        const nameComponent = container.querySelector(`#job-server-config-name-${i}`);
                        expect(nameComponent.value).toBe(testData[i].name);
                        const valueComponent = container.querySelector(`#job-server-config-value-${i}`);
                        expect(valueComponent.value).toBe(testData[i].value);
                    }
                });
            }
            it("does not process unknown file type", async () => {
                setupGetMocks();
                setupPostMocks();
                const { container } = render(<EditJob />);

                const jobServerConfig = container.querySelector("div#job-server-config");
                const uploadFileButton = jobServerConfig.querySelector("#job-server-config-uploader");

                const testData = [
                    { name: "test_name_1", value: "test_value_1" },
                    { name: "test_name_2", value: "test_value_2" },
                    { name: "test_name_3", value: "test_value_3" },
                ];
                const fileMock = {
                    name: "test.txt",
                    text: async () =>
                        "test_name_1: test_value_1\ntest_name_2: test_value_2\ntest_name_3: test_value_3\n",
                };

                await act(async () => fireEvent.change(uploadFileButton, { target: { files: [fileMock] } }));

                const nameComponent = container.querySelector(`#job-server-config-name-0`);
                expect(nameComponent.value).toBe("");
                const valueComponent = container.querySelector(`#job-server-config-value-0`);
                expect(valueComponent.value).toBe("");
            });
        });
    });

    describe("Client Info", () => {
        it("Render Correctly", () => {
            setupGetMocks();
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobClientsInfo = container.querySelector("div#job-clients-info");
            const header = jobClientsInfo.querySelector("h6");
            expect(header).toBeInTheDocument();
            expect(header).toHaveTextContent("Clients Configuration");
            const addButton = jobClientsInfo.querySelector("i#job-clients-info-add");
            expect(addButton).toBeInTheDocument();
            expect(addButton).toHaveTextContent("add");

            const jobClientInfoServiceAddress = container.querySelector("input#job-client-info-service-address-0");
            expect(jobClientInfoServiceAddress).toBeInTheDocument();
            expect(jobClientInfoServiceAddress.value).toBe("");

            const jobClientInfoDataPath = container.querySelector("input#job-client-info-data-path-0");
            expect(jobClientInfoDataPath).toBeInTheDocument();
            expect(jobClientInfoDataPath.value).toBe("");

            const jobClientInfoRedisAddress = container.querySelector("input#job-client-info-redis-address-0");
            expect(jobClientInfoRedisAddress).toBeInTheDocument();
            expect(jobClientInfoRedisAddress.value).toBe("");
        });
        it("Add button click adds a new element", () => {
            setupGetMocks();
            setupPostMocks();

            const { container } = render(<EditJob />);

            const jobClientsInfo = container.querySelector("div#job-clients-info");
            const addButton = jobClientsInfo.querySelector("i#job-clients-info-add");

            act(() => addButton.click());

            const jobClientInfoServiceAddress = container.querySelector("input#job-client-info-service-address-1");
            expect(jobClientInfoServiceAddress).toBeInTheDocument();
            expect(jobClientInfoServiceAddress.value).toBe("");

            const jobClientInfoDataPath = container.querySelector("input#job-client-info-data-path-1");
            expect(jobClientInfoDataPath).toBeInTheDocument();
            expect(jobClientInfoDataPath.value).toBe("");

            const jobClientInfoRedisAddress = container.querySelector("input#job-client-info-redis-address-1");
            expect(jobClientInfoRedisAddress).toBeInTheDocument();
            expect(jobClientInfoRedisAddress.value).toBe("");
        });
        it("Remove button click removed the clicked element", () => {
            setupPostMocks();
            const { container } = render(<EditJob />);

            const jobClientInfo = container.querySelector("div#job-clients-info");
            const removeButton = jobClientInfo.querySelector("i#job-client-info-remove-0");

            act(() => removeButton.click());

            const jobClientInfoClient = container.querySelector("input#job-client-info-client-0");
            expect(jobClientInfoClient).not.toBeInTheDocument();
            const jobClientInfoServiceAddress = container.querySelector("input#job-client-info-service-address-0");
            expect(jobClientInfoServiceAddress).not.toBeInTheDocument();
            const jobClientInfoDataPath = container.querySelector("input#job-client-info-data-path-0");
            expect(jobClientInfoDataPath).not.toBeInTheDocument();
            const jobClientInfoRedisHost = container.querySelector("input#job-client-info-redis-host-0");
            expect(jobClientInfoRedisHost).not.toBeInTheDocument();
            const jobClientInfoRedisPort = container.querySelector("input#job-client-info-redis-port-0");
            expect(jobClientInfoRedisPort).not.toBeInTheDocument();
        });
    });

    describe("Form Submit", () => {
        it("Submits data correctly", async () => {
            const testModelsData = ["TEST-MODEL-1", "TEST-MODEL-2"];
            const testClientsData = ["TEST-CLIENT-1", "TEST-CLIENT-2"];
            const testOptimizersData = ["TEST-OPTIMIZER-1", "TEST-OPTIMIZER-2"];
            const testStrategiesData = ["TEST-STRATEGY-1", "TEST-STRATEGY-2"];
            setupGetMocks(testModelsData, testClientsData, testStrategiesData, testOptimizersData);
            postMock = setupPostMocks();

            const { container } = render(<EditJob />);

            const addServerConfigButton = container.querySelector("i#job-server-config-add");
            const addClientsInfoButton = container.querySelector("i#job-clients-info-add");
            act(() => addServerConfigButton.click());
            act(() => addClientsInfoButton.click());

            const testJob = {
                model: "TEST-MODEL-2",
                strategy: "TEST-STRATEGY-2",
                optimizer: "TEST-OPTIMIZER-2",
                server_address: "test server address",
                redis_address: "test redis address",
                server_config: [
                    {
                        name: "test server config name 1",
                        value: "test server config value 1",
                    },
                    {
                        name: "test server config name 2",
                        value: "test server config value 2",
                    },
                ],
                client: "TEST-CLIENT-2",
                clients_info: [
                    {
                        service_address: "test service address 1",
                        data_path: "test data path 1",
                        redis_address: "test redis address 1",
                        hashed_password: "test hashed password 1",
                    },
                    {
                        service_address: "test service address 2",
                        data_path: "test data path 2",
                        redis_address: "test redis address 2",
                        hashed_password: "test hashed password 2",
                    },
                ],
            };

            const makeTargetValue = (value) => {
                return { target: { value: value } };
            };
            act(() => {
                fireEvent.change(container.querySelector("select#job-model"), makeTargetValue(testJob.model));
                fireEvent.change(container.querySelector("select#job-optimizer"), makeTargetValue(testJob.optimizer));
                fireEvent.change(container.querySelector("select#job-strategy"), makeTargetValue(testJob.strategy));
                fireEvent.change(container.querySelector("select#job-client"), makeTargetValue(testJob.client));
                fireEvent.change(
                    container.querySelector("input#job-server-address"),
                    makeTargetValue(testJob.server_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-redis-address"),
                    makeTargetValue(testJob.redis_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-server-config-name-0"),
                    makeTargetValue(testJob.server_config[0].name),
                );
                fireEvent.change(
                    container.querySelector("input#job-server-config-value-0"),
                    makeTargetValue(testJob.server_config[0].value),
                );
                fireEvent.change(
                    container.querySelector("input#job-server-config-name-1"),
                    makeTargetValue(testJob.server_config[1].name),
                );
                fireEvent.change(
                    container.querySelector("input#job-server-config-value-1"),
                    makeTargetValue(testJob.server_config[1].value),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-service-address-0"),
                    makeTargetValue(testJob.clients_info[0].service_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-data-path-0"),
                    makeTargetValue(testJob.clients_info[0].data_path),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-redis-address-0"),
                    makeTargetValue(testJob.clients_info[0].redis_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-password-0"),
                    makeTargetValue(testJob.clients_info[0].hashed_password),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-service-address-1"),
                    makeTargetValue(testJob.clients_info[1].service_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-data-path-1"),
                    makeTargetValue(testJob.clients_info[1].data_path),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-redis-address-1"),
                    makeTargetValue(testJob.clients_info[1].redis_address),
                );
                fireEvent.change(
                    container.querySelector("input#job-client-info-password-1"),
                    makeTargetValue(testJob.clients_info[1].hashed_password),
                );
            });

            const submitButton = container.querySelector("button#job-post");
            await act(async () => await submitButton.click());

            testJob.server_config = JSON.stringify({
                [testJob.server_config[0].name]: testJob.server_config[0].value,
                [testJob.server_config[1].name]: testJob.server_config[1].value,
            });
            testJob.clients_info[0].hashed_password = createHash("sha256").update(testJob.clients_info[0].hashed_password).digest("hex")
            testJob.clients_info[1].hashed_password = createHash("sha256").update(testJob.clients_info[1].hashed_password).digest("hex")
            expect(postMock).toBeCalledWith("/api/server/job", JSON.stringify(testJob));
        });

        it("Displays submit error", async () => {
            setupGetMocks();
            postMock = setupPostMocks({ error: true });

            const { container } = render(<EditJob />);

            const submitButton = container.querySelector("button#job-post");
            await act(async () => await submitButton.click());

            const testJob = makeEmptyJob();
            testJob.server_config = JSON.stringify({ "": "" });
            testJob.clients_info[0].hashed_password = createHash("sha256").update(testJob.clients_info[0].hashed_password).digest("hex")
            expect(postMock).toBeCalledWith("/api/server/job", JSON.stringify(testJob));

            const errorAlert = container.querySelector("div#job-save-error");
            expect(errorAlert).toBeInTheDocument();
        });

        it("Disables button when loading", async () => {
            setupGetMocks();
            postMock = setupPostMocks({ isLoading: true });

            const { container } = render(<EditJob />);

            const submitButton = container.querySelector("button#job-post");
            expect(submitButton).toBeInTheDocument();
            expect(submitButton.classList).toContain("disabled");
        });
    });
});
