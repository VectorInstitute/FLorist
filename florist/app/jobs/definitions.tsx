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
    redis_host: string;
    redis_port: string;
}
