"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfigFromEnv = loadConfigFromEnv;
exports.toClientConfig = toClientConfig;
exports.createClientFromEnv = createClientFromEnv;
const node_path_1 = __importDefault(require("node:path"));
const dotenv_1 = require("dotenv");
const client_1 = require("./client");
function loadConfigFromEnv(overrides = {}) {
    ensureEnvLoaded();
    const host = overrides.host ??
        process.env.HOME_ASSISTANT_HOST ??
        'http://localhost:8123';
    const token = overrides.token ?? process.env.HOME_ASSISTANT_TOKEN;
    if (!token) {
        throw new Error('HOME_ASSISTANT_TOKEN or an explicit token override is required.');
    }
    const timeoutEnv = process.env.HOME_ASSISTANT_TIMEOUT_MS;
    const timeoutMs = overrides.timeoutMs ??
        (timeoutEnv ? Number.parseInt(timeoutEnv, 10) : 10000);
    const insecureEnv = process.env.HOME_ASSISTANT_INSECURE;
    const insecure = overrides.insecure ??
        (insecureEnv === '1' || insecureEnv === 'true' || insecureEnv === 'yes');
    const debugEnv = process.env.HOME_ASSISTANT_DEBUG;
    const debug = overrides.debug ??
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
function ensureEnvLoaded() {
    if (envLoaded)
        return;
    envLoaded = true;
    const candidates = [
        node_path_1.default.resolve(process.cwd(), '.env'),
        node_path_1.default.resolve(__dirname, '../.env'),
        node_path_1.default.resolve(__dirname, '../../.env'),
    ];
    for (const candidate of candidates) {
        try {
            (0, dotenv_1.config)({ path: candidate, override: false });
        }
        catch {
            // Ignore errors when loading optional .env files
        }
    }
}
function toClientConfig(envConfig) {
    return {
        baseUrl: envConfig.host,
        token: envConfig.token,
        timeoutMs: envConfig.timeoutMs,
        insecure: envConfig.insecure,
        debug: envConfig.debug,
    };
}
function createClientFromEnv(overrides = {}) {
    const envConfig = loadConfigFromEnv(overrides);
    const clientConfig = toClientConfig(envConfig);
    return client_1.HomeAssistantClient.fromConfig(clientConfig);
}
