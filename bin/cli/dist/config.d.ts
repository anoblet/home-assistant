import { HomeAssistantClient, HomeAssistantClientConfig } from './client';
export interface EnvConfig {
    host: string;
    token: string;
    timeoutMs: number;
    insecure: boolean;
    debug: boolean;
}
export interface EnvOverrides {
    host?: string;
    token?: string;
    timeoutMs?: number;
    insecure?: boolean;
    debug?: boolean;
}
export declare function loadConfigFromEnv(overrides?: EnvOverrides): EnvConfig;
export declare function toClientConfig(envConfig: EnvConfig): HomeAssistantClientConfig;
export declare function createClientFromEnv(overrides?: EnvOverrides): HomeAssistantClient;
