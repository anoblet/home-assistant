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

export class HomeAssistantApiError extends Error {
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
  }) {
    super(params.message);
    this.name = 'HomeAssistantApiError';
    this.status = params.status;
    this.statusText = params.statusText;
    this.path = params.path;
    this.responseBody = params.responseBody;
  }
}

export class HttpClient {
  private readonly base: string;
  private readonly token: string;
  private readonly timeoutMs: number;
  private readonly debug: boolean;

  constructor(options: HttpClientOptions) {
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

  async getJson<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('GET', path, { ...options, responseType: 'json' });
  }

  async getText(path: string, options?: RequestOptions): Promise<string> {
    return this.request<string>('GET', path, { ...options, responseType: 'text' });
  }

  async getBinary(path: string, options?: RequestOptions): Promise<Uint8Array> {
    return this.request<Uint8Array>('GET', path, {
      ...options,
      responseType: 'binary',
    });
  }

  async postJson<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('POST', path, {
      ...options,
      body,
      responseType: 'json',
    });
  }

  async deleteJson<T = void>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('DELETE', path, { ...options, responseType: 'json' });
  }

  async request<T>(
    method: string,
    path: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const url = this.buildUrl(path, options.query);
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const controller = new AbortController();
    const timeout = this.timeoutMs;
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeout);

    const body =
      options.body === undefined || method === 'GET'
        ? undefined
        : JSON.stringify(options.body);

    if (this.debug) {
      // eslint-disable-next-line no-console
      console.error(
        `[ha-http] ${method} ${url} timeout=${timeout}ms body=${body ?? 'null'
        }`,
      );
    }

    let res: Response;
    try {
      res = await fetch(url, {
        method,
        headers,
        body,
        signal: controller.signal,
      });
    } catch (error) {
      if (
        error &&
        typeof error === 'object' &&
        'name' in error &&
        // AbortError is thrown when the request is aborted due to timeout.
        (error as { name?: unknown }).name === 'AbortError'
      ) {
        throw new Error(`Request timed out after ${timeout}ms: ${url}`);
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }

    const responseType = options.responseType ?? 'json';

    if (!res.ok) {
      let responseBody: string | undefined;
      try {
        responseBody = await res.text();
      } catch {
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
      return (await res.text()) as T;
    }

    if (responseType === 'binary') {
      const arrayBuffer = await res.arrayBuffer();
      return new Uint8Array(arrayBuffer) as T;
    }

    if (res.status === 204) {
      // No content
      return undefined as T;
    }

    return (await res.json()) as T;
  }

  private buildUrl(
    path: string,
    query?: Record<string, string | number | boolean | undefined>,
  ): string {
    const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
    const url = new URL(normalizedPath, this.base);

    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value === undefined) continue;
        url.searchParams.append(key, String(value));
      }
    }

    return url.toString();
  }
}
