import { config as loadDotEnv } from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { HomeAssistantClientConfig } from './client.ts';
import { HomeAssistantClient } from './client.ts';

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

  const debugEnv = process.env.HOME_ASSISTANT_DEBUG;
  const debug = overrides.debug ?? parseBooleanEnv(debugEnv);

  const host = overrides.host ?? process.env.HOME_ASSISTANT_HOST ?? 'http://localhost:8123';

  const token = overrides.token ?? process.env.HOME_ASSISTANT_TOKEN;

  if (!token) {
    throw new Error('HOME_ASSISTANT_TOKEN or an explicit token override is required.');
  }

  const timeoutEnv = process.env.HOME_ASSISTANT_TIMEOUT_MS;
  const timeoutMs = normalizeTimeoutMs({
    override: overrides.timeoutMs,
    envValue: timeoutEnv,
    debug,
    defaultValue: 10000,
  });

  const insecureEnv = process.env.HOME_ASSISTANT_INSECURE;
  const insecure =
    overrides.insecure ?? (insecureEnv === '1' || insecureEnv === 'true' || insecureEnv === 'yes');

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

function parseBooleanEnv(value: string | undefined): boolean {
  return value === '1' || value === 'true' || value === 'yes';
}

function normalizeTimeoutMs(params: {
  override: number | undefined;
  envValue: string | undefined;
  debug: boolean;
  defaultValue: number;
}): number {
  const { override, envValue, debug, defaultValue } = params;

  const parsedOverride = override !== undefined && Number.isFinite(override) ? override : undefined;
  if (parsedOverride !== undefined) {
    if (parsedOverride > 0) return Math.trunc(parsedOverride);
    if (debug) {
      // eslint-disable-next-line no-console
      console.error(
        `[ha-cli] Invalid timeout override (${String(override)}); falling back to ${defaultValue}ms`
      );
    }
    return defaultValue;
  }

  if (!envValue) return defaultValue;
  const envTrimmed = envValue.trim();
  if (!envTrimmed) return defaultValue;
  if (!/^\d+$/.test(envTrimmed)) {
    if (debug) {
      // eslint-disable-next-line no-console
      console.error(
        `[ha-cli] Invalid HOME_ASSISTANT_TIMEOUT_MS (${envValue}); falling back to ${defaultValue}ms`
      );
    }
    return defaultValue;
  }

  const parsedEnv = Number.parseInt(envTrimmed, 10);
  if (!Number.isFinite(parsedEnv) || parsedEnv <= 0) {
    if (debug) {
      // eslint-disable-next-line no-console
      console.error(
        `[ha-cli] Invalid HOME_ASSISTANT_TIMEOUT_MS (${envValue}); falling back to ${defaultValue}ms`
      );
    }
    return defaultValue;
  }

  return parsedEnv;
}

let envLoaded = false;

function ensureEnvLoaded(): void {
  if (envLoaded) return;
  envLoaded = true;

  const moduleDir = path.dirname(fileURLToPath(import.meta.url));

  const candidates: string[] = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(moduleDir, '../.env'),
    path.resolve(moduleDir, '../../.env'),
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

export function createClientFromEnv(overrides: EnvOverrides = {}): HomeAssistantClient {
  const envConfig = loadConfigFromEnv(overrides);
  const clientConfig = toClientConfig(envConfig);
  return HomeAssistantClient.fromConfig(clientConfig);
}
