# `home-assistant` – Home Assistant REST API CLI

A small TypeScript client and CLI for the [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/), integrated into this Home Assistant configuration repo.

The CLI is built around the official REST endpoints:

- `GET /api/` – API overview
- `GET /api/config` – Core configuration
- `GET /api/components` – Loaded components
- `GET /api/events` / `POST /api/events/<event_type>` – Events
- `GET /api/services` / `POST /api/services/<domain>/<service>` – Services
- `GET /api/states` / `GET|POST|DELETE /api/states/<entity_id>` – States
- `GET /api/history/period/<timestamp>` – History
- `GET /api/logbook/<timestamp>` – Logbook
- `GET /api/error_log` – Error log
- `GET /api/camera_proxy/<camera entity_id>` – Camera snapshot
- `GET /api/calendars` / `GET /api/calendars/<calendar entity_id>?start=<timestamp>&end=<timestamp>` – Calendars
- `POST /api/template` – Template rendering
- `POST /api/config/core/check_config` – Config validation
- `POST /api/intent/handle` – Intent handling
- Plus a `raw request` command for any future/undocumented endpoints.

## Configuration & Authentication

The CLI and client use environment variables by default:

- `HOME_ASSISTANT_HOST` – Base URL, e.g. `http://localhost:8123`
- `HOME_ASSISTANT_TOKEN` – Long‑lived access token
- `HOME_ASSISTANT_TIMEOUT_MS` – Optional request timeout in milliseconds (digits-only, default `10000`)
- `HOME_ASSISTANT_INSECURE` – Set to `1`/`true`/`yes` to allow self‑signed TLS
- `HOME_ASSISTANT_DEBUG` – Set to `1`/`true`/`yes` for debug logging

You can use the included env template:

```bash
cp bin/cli/.env.example .env
```

CLI flags can override env vars:

- `-H, --host <url>` – Base URL override
- `-T, --token <token>` – Token override
- `--timeout <ms>` – Timeout override in milliseconds (digits-only)
- `-k, --insecure` – Allow self‑signed TLS
- `-o, --output <file>` – Write output to a file instead of stdout
- `--pretty` – Pretty‑print JSON
- `--debug` – Extra debug logging (HTTP request logging + stack traces)

## Runtime Requirements

- Node.js `>= 22.6` (built-in `fetch` + native TypeScript type-stripping)

The CLI runs directly from TypeScript sources (no build step required). The published `home-assistant` binary is a tiny shim that invokes Node with `--experimental-strip-types`.

## Installing

From the repo root:

```bash
pnpm install
```

You can run the CLI without a global install from the repo root:

```bash
# Recommended: run via pnpm against the cli package
pnpm --filter cli home-assistant --help

# Or via the root-level helper script
pnpm home-assistant --help
```

`pnpm --filter cli build` runs a TypeScript typecheck (`tsc --noEmit`).

## Testing

Run the CLI tests directly from TypeScript sources:

```bash
pnpm --filter cli test
```

## Behavior Contract (Stability)

- Invalid `HOME_ASSISTANT_TIMEOUT_MS` values fall back to the default (`10000`).
- Invalid `--timeout <ms>` values fail fast as a usage error.
- Absolute URLs are rejected; provide an API path like `/api/config`.
- Errors are written to stderr.
- Stack traces are only shown when `--debug` or `HOME_ASSISTANT_DEBUG` is enabled.

## Programmatic TypeScript Usage

```ts
import { createClientFromEnv } from 'cli';

async function main() {
  const client = createClientFromEnv();
  const info = await client.getApiOverview();
  console.log(info);
}

main().catch(console.error);
```

> Note: this repo is a pnpm workspace; the package name is `cli` and the public API is exported from `src/index.ts`.

## Endpoint‑Level Examples

In all examples below, CLI invocations assume `HOME_ASSISTANT_HOST` and `HOME_ASSISTANT_TOKEN` are set.

### Core API

- CLI: `GET /api/`

```bash
home-assistant api info --pretty
```

- TS:

```ts
const info = await client.getApiOverview();
```

### Configuration

- CLI: `GET /api/config`

```bash
home-assistant config get --pretty
```

- TS:

```ts
const config = await client.getConfig();
```

- CLI: `POST /api/config/core/check_config`

```bash
home-assistant config check --pretty
```

- TS:

```ts
const result = await client.checkConfig();
```

### Components

- CLI: `GET /api/components`

```bash
home-assistant components --pretty
```

- TS:

```ts
const components = await client.getComponents();
```

### Events

- CLI: `GET /api/events`

```bash
home-assistant events list --pretty
```

- CLI: `POST /api/events/<event_type>`

```bash
home-assistant events fire my_custom_event --data '{"foo":"bar"}'
```

- TS:

```ts
const events = await client.getEvents();
await client.fireEvent('my_custom_event', { foo: 'bar' });
```

### Services

- CLI: `GET /api/services`

```bash
home-assistant services list --pretty
```

- CLI: `POST /api/services/<domain>/<service>`

```bash
home-assistant services call light turn_on --data '{"entity_id":"light.kitchen"}'
```

- TS:

```ts
const services = await client.getServices();
await client.callService('light', 'turn_on', { entity_id: 'light.kitchen' });
```

### States

- CLI: `GET /api/states`

```bash
home-assistant states list --pretty
```

- CLI: `GET /api/states/<entity_id>`

```bash
home-assistant states get light.kitchen --pretty
```

- CLI: `POST /api/states/<entity_id>`

```bash
home-assistant states set sensor.demo on --attributes '{"friendly_name":"Demo"}'
```

- CLI: `DELETE /api/states/<entity_id>`

```bash
home-assistant states delete sensor.demo
```

- TS:

```ts
const allStates = await client.getStates();
const state = await client.getState('light.kitchen');
await client.setState('sensor.demo', 'on', { friendly_name: 'Demo' });
await client.deleteState('sensor.demo');
```

### History

- CLI: `GET /api/history/period/<timestamp>`

```bash
home-assistant history get 2025-01-01T00:00:00Z \
  --end 2025-01-01T06:00:00Z \
  --entity-id light.kitchen sensor.demo \
  --minimal --no-attributes --pretty
```

- TS:

```ts
const history = await client.getHistory('2025-01-01T00:00:00Z', {
  end_time: '2025-01-01T06:00:00Z',
  filter_entity_id: ['light.kitchen', 'sensor.demo'],
  minimal_response: true,
  no_attributes: true,
});
```

### Logbook

- CLI: `GET /api/logbook/<timestamp>`

```bash
home-assistant logbook get 2025-01-01T00:00:00Z \
  --end 2025-01-01T06:00:00Z \
  --entity light.kitchen --pretty
```

- TS:

```ts
const entries = await client.getLogbook('2025-01-01T00:00:00Z', {
  end_time: '2025-01-01T06:00:00Z',
  entity: 'light.kitchen',
});
```

### Error Log

- CLI: `GET /api/error_log`

```bash
home-assistant error-log
```

- TS:

```ts
const log = await client.getErrorLog();
console.log(log);
```

### Camera Proxy

- CLI: `GET /api/camera_proxy/<camera entity_id>`

```bash
# Write JPEG to a file
home-assistant camera snapshot camera.front_door -o /tmp/front-door.jpg

# Or stream to stdout and redirect
home-assistant camera snapshot camera.front_door > /tmp/front-door.jpg
```

- TS:

```ts
const image = await client.getCameraImage('camera.front_door');
// image is a Uint8Array containing the JPEG bytes
```

### Calendars

- CLI: `GET /api/calendars`

```bash
home-assistant calendars list --pretty
```

- CLI: `GET /api/calendars/<calendar entity_id>?start=<timestamp>&end=<timestamp>`

```bash
home-assistant calendars events calendar.personal \
  --start 2025-01-01T00:00:00Z \
  --end 2025-01-02T00:00:00Z \
  --pretty
```

- TS:

```ts
const calendars = await client.getCalendars();
const events = await client.getCalendarEvents(
  'calendar.personal',
  '2025-01-01T00:00:00Z',
  '2025-01-02T00:00:00Z'
);
```

### Templates

- CLI: `POST /api/template`

```bash
home-assistant template render --template 'Hello {{ states("sensor.time") }}'

echo 'Hello {{ states("sensor.time") }}' | home-assistant template render
```

- TS:

```ts
const rendered = await client.renderTemplate({
  template: 'Hello {{ states("sensor.time") }}',
});
```

### Config Check

- CLI: `POST /api/config/core/check_config`

```bash
home-assistant config check --pretty
```

- TS:

```ts
const result = await client.checkConfig();
```

### Intent Handling

- CLI: `POST /api/intent/handle`

```bash
home-assistant intent handle --payload '{"name":"HassTurnOn","data":{"entity_id":"light.kitchen"}}'
```

- TS:

```ts
const response = await client.handleIntent({
  name: 'HassTurnOn',
  data: { entity_id: 'light.kitchen' },
});
```

### Raw Requests

For future REST endpoints or debugging, you can use the raw request helper.

- CLI:

```bash
home-assistant raw request GET /api/config --pretty
home-assistant raw request POST /api/services/light/turn_on \
  --body '{"entity_id":"light.kitchen"}' --pretty
```

- TS:

```ts
const configRaw = await client.rawRequest('GET', '/api/config', {
  responseType: 'json',
});

await client.rawRequest('POST', '/api/services/light/turn_on', {
  body: { entity_id: 'light.kitchen' },
});
```

## Smoke Test

A minimal smoke test script is provided to exercise key endpoints.

From the repo root (with `HOME_ASSISTANT_HOST` and `HOME_ASSISTANT_TOKEN` set):

```bash
pnpm --filter cli smoke
```

This will call `/api/`, `/api/config`, and `/api/states` and print basic information.
