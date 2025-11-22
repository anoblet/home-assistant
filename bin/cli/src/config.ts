import path from 'node:path';
import { config as loadDotEnv } from 'dotenv';
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

export function loadConfigFromEnv(overrides: EnvOverrides = {}): EnvConfig {
  ensureEnvLoaded();

  const host =
    overrides.host ??
    process.env.HOME_ASSISTANT_HOST ??
    'http://localhost:8123';

  const token = overrides.token ?? process.env.HOME_ASSISTANT_TOKEN;

  if (!token) {
    throw new Error(
      'HOME_ASSISTANT_TOKEN or an explicit token override is required.',
    );
  }

  const timeoutEnv = process.env.HOME_ASSISTANT_TIMEOUT_MS;
  const timeoutMs = overrides.timeoutMs ??
    (timeoutEnv ? Number.parseInt(timeoutEnv, 10) : 10000);

  const insecureEnv = process.env.HOME_ASSISTANT_INSECURE;
  const insecure =
    overrides.insecure ??
    (insecureEnv === '1' || insecureEnv === 'true' || insecureEnv === 'yes');

  const debugEnv = process.env.HOME_ASSISTANT_DEBUG;
  const debug =
    overrides.debug ??
    (debugEnv === '1' || debugEnv === 'true' || debugEnv === 'yes');

  if (insecure) {
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
  }

  return {
    host,
    token,
    timeoutMs,
    insecure,
    debug,
  };
}

let envLoaded = false;

function ensureEnvLoaded(): void {
  if (envLoaded) return;
  envLoaded = true;

  const candidates: string[] = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(__dirname, '../.env'),
    path.resolve(__dirname, '../../.env'),
  ];

  for (const candidate of candidates) {
    try {
      loadDotEnv({ path: candidate, override: false });
    } catch {
      // Ignore errors when loading optional .env files
    }
  }
}

export function toClientConfig(envConfig: EnvConfig): HomeAssistantClientConfig {
  return {
    baseUrl: envConfig.host,
    token: envConfig.token,
    timeoutMs: envConfig.timeoutMs,
    insecure: envConfig.insecure,
    debug: envConfig.debug,
  };
}

export function createClientFromEnv(
  overrides: EnvOverrides = {},
): HomeAssistantClient {
  const envConfig = loadConfigFromEnv(overrides);
  const clientConfig = toClientConfig(envConfig);
  return HomeAssistantClient.fromConfig(clientConfig);
}
