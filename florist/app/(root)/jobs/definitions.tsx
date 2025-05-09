// Must be in same order as array returned from useGetJobsByJobStatus
export const validStatuses = {
    NOT_STARTED: "Not Started",
    IN_PROGRESS: "In Progress",
    FINISHED_SUCCESSFULLY: "Finished Successfully",
    FINISHED_WITH_ERROR: "Finished with Error",
};

export interface Job {
    _id?: string;
    status?: string;
    model: string;
    strategy: string;
    optimizer: string;
    server_address: string;
    server_config: Array<ServerConfig>;
    redis_address: string;
    client: string;
    clients_info: Array<ClientInfo>;
}

export interface ServerConfig {
    name: string;
    value: string;
}

export interface ClientInfo {
    service_address: string;
    data_path: string;
    redis_address: string;
    hashed_password: string;
    metrics?: string;
}

export interface Metrics {
    [key: string]: any;
    host_type: "server" | "client";
    rounds: RoundMetrics[];
}

export interface RoundMetrics {
    [key: string]: any;
    fit_start: string;
    fit_end: string;
    fit_round_start: string;
    fit_round_end: string;
    eval_start: string;
    eval_end: string;
    eval_round_start: string;
    eval_round_end: string;
}

export interface JobDetailsProperties {
    jobId?: string;
    jobStatus?: keyof typeof validStatuses;
    totalEpochs?: number;
}

export interface ServerConfigDict {
    [key: string]: any;
}
