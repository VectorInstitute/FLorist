// Must be in same order as array returned from useGetJobsByJobStatus
export const validStatuses = {
    NOT_STARTED: "Not Started",
    IN_PROGRESS: "In Progress",
    FINISHED_SUCCESSFULLY: "Finished Successfully",
    FINISHED_WITH_ERROR: "Finished with Error",
};

export interface JobData {
    _id: string;
    status: string;
    model: string;
    server_address: string;
    server_info: string;
    redis_host: string;
    redis_port: string;
    clients_info: Array<ClientInfo>;
}

export interface ClientInfo {
    client: string;
    service_address: string;
    data_path: string;
    redis_address: string;
    metrics: string;
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
