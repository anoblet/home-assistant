"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpClient = exports.HomeAssistantApiError = void 0;
class HomeAssistantApiError extends Error {
    constructor(params) {
        super(params.message);
        this.name = 'HomeAssistantApiError';
        this.status = params.status;
        this.statusText = params.statusText;
        this.path = params.path;
        this.responseBody = params.responseBody;
    }
}
exports.HomeAssistantApiError = HomeAssistantApiError;
class HttpClient {
    constructor(options) {
        if (!options.baseUrl) {
            throw new Error('HttpClient requires a baseUrl');
        }
        if (!options.token) {
            throw new Error('HttpClient requires an authentication token');
        }
        this.base = options.baseUrl.endsWith('/')
            ? options.baseUrl
            : `${options.baseUrl}/`;
        this.token = options.token;
        this.timeoutMs = options.timeoutMs ?? 10000;
        this.debug = !!options.debug;
        if (options.insecure) {
            // Allow self-signed certificates for this process when explicitly requested.
            // This mirrors curl's --insecure behaviour and is limited to this CLI process.
            process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
        }
    }
    async getJson(path, options) {
        return this.request('GET', path, { ...options, responseType: 'json' });
    }
    async getText(path, options) {
        return this.request('GET', path, { ...options, responseType: 'text' });
    }
    async getBinary(path, options) {
        return this.request('GET', path, {
            ...options,
            responseType: 'binary',
        });
    }
    async postJson(path, body, options) {
        return this.request('POST', path, {
            ...options,
            body,
            responseType: 'json',
        });
    }
    async deleteJson(path, options) {
        return this.request('DELETE', path, { ...options, responseType: 'json' });
    }
    async request(method, path, options = {}) {
        const url = this.buildUrl(path, options.query);
        const headers = {
            Authorization: `Bearer ${this.token}`,
            'Content-Type': 'application/json',
            ...options.headers,
        };
        const controller = new AbortController();
        const timeout = this.timeoutMs;
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, timeout);
        const body = options.body === undefined || method === 'GET'
            ? undefined
            : JSON.stringify(options.body);
        if (this.debug) {
            // eslint-disable-next-line no-console
            console.error(`[ha-http] ${method} ${url} timeout=${timeout}ms body=${body ?? 'null'}`);
        }
        let res;
        try {
            res = await fetch(url, {
                method,
                headers,
                body,
                signal: controller.signal,
            });
        }
        catch (error) {
            if (error &&
                typeof error === 'object' &&
                'name' in error &&
                // AbortError is thrown when the request is aborted due to timeout.
                error.name === 'AbortError') {
                throw new Error(`Request timed out after ${timeout}ms: ${url}`);
            }
            throw error;
        }
        finally {
            clearTimeout(timeoutId);
        }
        const responseType = options.responseType ?? 'json';
        if (!res.ok) {
            let responseBody;
            try {
                responseBody = await res.text();
            }
            catch {
                // ignore
            }
            throw new HomeAssistantApiError({
                message: `Home Assistant API request failed with status ${res.status} ${res.statusText}`,
                status: res.status,
                statusText: res.statusText,
                path,
                responseBody,
            });
        }
        if (responseType === 'text') {
            return (await res.text());
        }
        if (responseType === 'binary') {
            const arrayBuffer = await res.arrayBuffer();
            return new Uint8Array(arrayBuffer);
        }
        if (res.status === 204) {
            // No content
            return undefined;
        }
        return (await res.json());
    }
    buildUrl(path, query) {
        const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
        const url = new URL(normalizedPath, this.base);
        if (query) {
            for (const [key, value] of Object.entries(query)) {
                if (value === undefined)
                    continue;
                url.searchParams.append(key, String(value));
            }
        }
        return url.toString();
    }
}
exports.HttpClient = HttpClient;
