export interface HttpClientOptions {
    baseUrl: string;
    token: string;
    timeoutMs?: number;
    insecure?: boolean;
    debug?: boolean;
}
export type ResponseType = 'json' | 'text' | 'binary';
export interface RequestOptions {
    query?: Record<string, string | number | boolean | undefined>;
    body?: unknown;
    headers?: Record<string, string>;
    responseType?: ResponseType;
}
export declare class HomeAssistantApiError extends Error {
    readonly status: number;
    readonly statusText: string;
    readonly path: string;
    readonly responseBody?: string;
    constructor(params: {
        message: string;
        status: number;
        statusText: string;
        path: string;
        responseBody?: string;
    });
}
export declare class HttpClient {
    private readonly base;
    private readonly token;
    private readonly timeoutMs;
    private readonly debug;
    constructor(options: HttpClientOptions);
    getJson<T>(path: string, options?: RequestOptions): Promise<T>;
    getText(path: string, options?: RequestOptions): Promise<string>;
    getBinary(path: string, options?: RequestOptions): Promise<Uint8Array>;
    postJson<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T>;
    deleteJson<T = void>(path: string, options?: RequestOptions): Promise<T>;
    request<T>(method: string, path: string, options?: RequestOptions): Promise<T>;
    private buildUrl;
}
