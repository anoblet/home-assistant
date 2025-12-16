import { Command, CommanderError, InvalidArgumentError } from 'commander';
import { promises as fs } from 'node:fs';
import type { RequestOptions } from './client.ts';
import { HomeAssistantApiError, HomeAssistantClient } from './client.ts';
import type { EnvOverrides } from './config.ts';
import { createClientFromEnv } from './config.ts';

interface GlobalCliOptions {
  host?: string;
  token?: string;
  timeout?: number;
  insecure?: boolean;
  output?: string;
  pretty?: boolean;
  debug?: boolean;
}

interface OutputOptions {
  format?: 'json' | 'text' | 'binary';
}

async function writeOutput(
  data: unknown,
  cmd: Command,
  options: OutputOptions = {}
): Promise<void> {
  const opts = cmd.optsWithGlobals() as GlobalCliOptions;
  const outputPath = opts.output;
  const format = options.format ?? 'json';

  if (format === 'binary') {
    const buffer =
      data instanceof Uint8Array ? Buffer.from(data) : Buffer.from(data as ArrayBuffer);

    if (outputPath) {
      await fs.writeFile(outputPath, buffer);
    } else {
      process.stdout.write(buffer);
    }

    return;
  }

  const text =
    format === 'text' ? String(data ?? '') : JSON.stringify(data, null, opts.pretty ? 2 : 0);

  if (outputPath) {
    await fs.writeFile(outputPath, text, 'utf8');
  } else {
    process.stdout.write(text);
    if (!text.endsWith('\n')) {
      process.stdout.write('\n');
    }
  }
}

function readJsonOrThrow(json?: string): unknown {
  if (!json) return undefined;
  try {
    return JSON.parse(json);
  } catch (error) {
    throw new Error(`Failed to parse JSON: ${(error as Error).message}`);
  }
}

function parseBooleanEnv(value: string | undefined): boolean {
  return value === '1' || value === 'true' || value === 'yes';
}

function isDebugEnabled(cmd?: Command): boolean {
  if (cmd) {
    const opts = cmd.optsWithGlobals() as GlobalCliOptions;
    if (opts.debug) return true;
  }
  return parseBooleanEnv(process.env.HOME_ASSISTANT_DEBUG);
}

function parseTimeoutMs(value: string): number {
  const trimmed = value.trim();
  if (!/^\d+$/.test(trimmed)) {
    throw new InvalidArgumentError('Timeout must be a positive integer (ms).');
  }
  const parsed = Number.parseInt(trimmed, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new InvalidArgumentError('Timeout must be a positive integer (ms).');
  }
  return parsed;
}

function buildEnvOverrides(opts: GlobalCliOptions): EnvOverrides {
  return {
    host: opts.host,
    token: opts.token,
    timeoutMs: opts.timeout,
    insecure: opts.insecure,
    debug: opts.debug,
  };
}

function createClientFromCommand(cmd: Command): HomeAssistantClient {
  const opts = cmd.optsWithGlobals() as GlobalCliOptions;
  const overrides = buildEnvOverrides(opts);
  return createClientFromEnv(overrides);
}

function handleCliError(
  error: unknown,
  options: {
    debug?: boolean;
  } = {}
): void {
  const debug = !!options.debug;

  if (error instanceof HomeAssistantApiError) {
    // eslint-disable-next-line no-console
    console.error(
      `Home Assistant API error (${error.status} ${error.statusText}) for ${error.path}`
    );
    if (error.responseBody) {
      // eslint-disable-next-line no-console
      console.error(error.responseBody);
    }
  } else if (error instanceof Error) {
    // eslint-disable-next-line no-console
    console.error(error.message);
  } else {
    // eslint-disable-next-line no-console
    console.error(String(error));
  }

  if (debug && error instanceof Error && error.stack) {
    // eslint-disable-next-line no-console
    console.error(error.stack);
  }

  process.exitCode = 1;
}

function actionWithClient<Args extends unknown[]>(
  handler: (client: HomeAssistantClient, cmd: Command, ...args: Args) => Promise<unknown> | unknown,
  outputOptions?: OutputOptions
) {
  return async function action(this: Command, ...args: Args): Promise<void> {
    const cmd = this;
    try {
      const client = createClientFromCommand(cmd);
      const result = await handler(client, cmd, ...(args as Args));
      if (result !== undefined) {
        await writeOutput(result, cmd, outputOptions);
      }
    } catch (error) {
      handleCliError(error, { debug: isDebugEnabled(cmd) });
    }
  };
}

async function readStdin(): Promise<string> {
  if (process.stdin.isTTY) {
    return '';
  }

  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk);
  }

  return Buffer.concat(chunks).toString('utf8');
}

export async function main(argv: string[] = process.argv): Promise<void> {
  const program = new Command();

  program.exitOverride();
  program.configureOutput({
    writeOut: (str) => process.stdout.write(str),
    writeErr: (str) => process.stderr.write(str),
  });

  program
    .name('home-assistant')
    .description('Home Assistant REST API CLI')
    .option(
      '-H, --host <url>',
      'Home Assistant base URL (default: HOME_ASSISTANT_HOST or http://localhost:8123)'
    )
    .option('-T, --token <token>', 'Long-lived access token (HOME_ASSISTANT_TOKEN)')
    .option('--timeout <ms>', 'Request timeout in milliseconds (digits-only)', parseTimeoutMs)
    .option('-k, --insecure', 'Allow insecure TLS (self-signed certificates)')
    .option('-o, --output <file>', 'Write output to file instead of stdout')
    .option('--pretty', 'Pretty-print JSON output')
    .option('--debug', 'Enable debug logging');

  // Core
  const api = program.command('api').description('Core API information');

  api
    .command('info')
    .description('Get API overview (/api/)')
    .action(actionWithClient((client) => client.getApiOverview()));

  const config = program.command('config').description('Configuration operations');

  config
    .command('get')
    .description('Get Home Assistant configuration (/api/config)')
    .action(actionWithClient((client) => client.getConfig()));

  config
    .command('check')
    .description('Validate configuration (/api/config/core/check_config)')
    .action(actionWithClient((client) => client.checkConfig()));

  program
    .command('components')
    .description('List loaded components (/api/components)')
    .action(actionWithClient((client) => client.getComponents()));

  // Events
  const events = program.command('events').description('Event operations');

  events
    .command('list')
    .description('List events (/api/events)')
    .action(actionWithClient((client) => client.getEvents()));

  events
    .command('fire')
    .description('Fire an event (/api/events/<event_type>)')
    .argument('<event_type>', 'Event type')
    .option('-d, --data <json>', 'JSON payload for the event data')
    .action(
      actionWithClient((client, cmd, eventType: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          data?: string;
        };
        const eventData = readJsonOrThrow(opts.data) as Record<string, unknown> | undefined;
        return client.fireEvent(eventType, eventData);
      })
    );

  // Services
  const services = program.command('services').description('Service operations');

  services
    .command('list')
    .description('List services (/api/services)')
    .action(actionWithClient((client) => client.getServices()));

  services
    .command('call')
    .description('Call a service (/api/services/<domain>/<service>)')
    .argument('<domain>', 'Service domain')
    .argument('<service>', 'Service name')
    .option('-d, --data <json>', 'JSON payload for the service call')
    .action(
      actionWithClient((client, cmd, domain: string, service: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          data?: string;
        };
        const serviceData = readJsonOrThrow(opts.data) as Record<string, unknown> | undefined;
        return client.callService(domain, service, serviceData);
      })
    );

  // States
  const states = program.command('states').description('State operations');

  states
    .command('list')
    .description('List all states (/api/states)')
    .action(actionWithClient((client) => client.getStates()));

  states
    .command('get')
    .description('Get state for an entity (/api/states/<entity_id>)')
    .argument('<entity_id>', 'Entity ID')
    .action(actionWithClient((client, _cmd, entityId: string) => client.getState(entityId)));

  states
    .command('set')
    .description('Set state for an entity (/api/states/<entity_id>)')
    .argument('<entity_id>', 'Entity ID')
    .argument('<state>', 'State value')
    .option('-a, --attributes <json>', 'JSON attributes object')
    .action(
      actionWithClient((client, cmd, entityId: string, state: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          attributes?: string;
        };
        const attributes = readJsonOrThrow(opts.attributes) as Record<string, unknown> | undefined;
        return client.setState(entityId, state, attributes);
      })
    );

  states
    .command('delete')
    .description('Delete state for an entity (/api/states/<entity_id>)')
    .argument('<entity_id>', 'Entity ID')
    .action(actionWithClient((client, _cmd, entityId: string) => client.deleteState(entityId)));

  // History
  const history = program.command('history').description('History operations');

  history
    .command('get')
    .description('Get history (/api/history/period/<timestamp>)')
    .argument('<start>', 'ISO8601 start timestamp')
    .option('--end <timestamp>', 'ISO8601 end timestamp')
    .option('--entity-id <entity_id...>', 'Filter by one or more entity IDs')
    .option('--minimal', 'Return minimal response without attributes')
    .option('--no-attributes', 'Exclude attributes from the response')
    .action(
      actionWithClient((client, cmd, start: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          end?: string;
          entityId?: string[];
          minimal?: boolean;
          noAttributes?: boolean;
        };

        return client.getHistory(start, {
          end_time: opts.end,
          filter_entity_id: opts.entityId,
          minimal_response: opts.minimal,
          no_attributes: opts.noAttributes,
        });
      })
    );

  // Logbook
  const logbook = program.command('logbook').description('Logbook operations');

  logbook
    .command('get')
    .description('Get logbook entries (/api/logbook/<timestamp>)')
    .argument('<start>', 'ISO8601 start timestamp')
    .option('--end <timestamp>', 'ISO8601 end timestamp')
    .option('--entity <entity_id>', 'Filter by entity ID')
    .option('--context-id <id>', 'Filter by context ID')
    .action(
      actionWithClient((client, cmd, start: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          end?: string;
          entity?: string;
          contextId?: string;
        };

        return client.getLogbook(start, {
          end_time: opts.end,
          entity: opts.entity,
          context_id: opts.contextId,
        });
      })
    );

  // Error log
  program
    .command('error-log')
    .description('Get error log (/api/error_log)')
    .action(actionWithClient((client) => client.getErrorLog(), { format: 'text' }));

  // Camera
  const camera = program.command('camera').description('Camera operations');

  camera
    .command('snapshot')
    .description('Get camera snapshot (/api/camera_proxy/<entity_id>)')
    .argument('<entity_id>', 'Camera entity ID')
    .action(
      actionWithClient(
        async (client, cmd, entityId: string) => {
          const image = await client.getCameraImage(entityId);
          await writeOutput(image, cmd, { format: 'binary' });
        },
        { format: 'binary' }
      )
    );

  // Calendars
  const calendars = program.command('calendars').description('Calendar operations');

  calendars
    .command('list')
    .description('List calendars (/api/calendars)')
    .action(actionWithClient((client) => client.getCalendars()));

  calendars
    .command('events')
    .description(
      'Get calendar events (/api/calendars/<entity_id>?start=<timestamp>&end=<timestamp>)'
    )
    .argument('<entity_id>', 'Calendar entity ID')
    .requiredOption('--start <timestamp>', 'ISO8601 start timestamp')
    .requiredOption('--end <timestamp>', 'ISO8601 end timestamp')
    .action(
      actionWithClient((client, cmd, entityId: string) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          start: string;
          end: string;
        };

        return client.getCalendarEvents(entityId, opts.start, opts.end);
      })
    );

  // Templates
  const template = program.command('template').description('Template operations');

  template
    .command('render')
    .description('Render a template (/api/template)')
    .option('-t, --template <template>', 'Template string')
    .option('-f, --file <path>', 'Template file path')
    .option('-v, --variables <json>', 'JSON variables object')
    .action(
      actionWithClient(async (client, cmd) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          template?: string;
          file?: string;
          variables?: string;
        };

        let templateString = opts.template;
        if (!templateString && opts.file) {
          templateString = await fs.readFile(opts.file, 'utf8');
        }

        if (!templateString) {
          const stdin = await readStdin();
          templateString = stdin.trim();
        }

        if (!templateString) {
          throw new Error('Template content is required (use --template, --file, or stdin).');
        }

        const variables = readJsonOrThrow(opts.variables) as Record<string, unknown> | undefined;

        return client.renderTemplate({
          template: templateString,
          variables,
        });
      })
    );

  // Intents
  const intent = program.command('intent').description('Intent operations');

  intent
    .command('handle')
    .description('Handle an intent (/api/intent/handle)')
    .option('-p, --payload <json>', 'JSON intent payload')
    .option('-f, --file <path>', 'JSON file with intent payload')
    .action(
      actionWithClient(async (client, cmd) => {
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          payload?: string;
          file?: string;
        };

        let payload: unknown = undefined;
        if (opts.payload) {
          payload = readJsonOrThrow(opts.payload);
        } else if (opts.file) {
          const text = await fs.readFile(opts.file, 'utf8');
          payload = readJsonOrThrow(text);
        } else {
          const stdin = await readStdin();
          if (stdin.trim()) {
            payload = readJsonOrThrow(stdin);
          }
        }

        if (!payload || typeof payload !== 'object') {
          throw new Error('Intent payload must be a JSON object.');
        }

        return client.handleIntent(payload as any);
      })
    );

  // Raw requests
  const raw = program.command('raw').description('Raw HTTP operations');

  raw
    .command('request')
    .description('Perform a raw HTTP request')
    .argument('<method>', 'HTTP method (GET, POST, DELETE, etc.)')
    .argument('<path>', 'Request path, e.g. /api/config')
    .option('-q, --query <json>', 'JSON object with query parameters')
    .option('-b, --body <json>', 'JSON request body')
    .option('--text', 'Treat response as plain text')
    .option('--binary', 'Treat response as binary data')
    .action(async function (this: Command, method: string, path: string) {
      const cmd = this;
      try {
        const client = createClientFromCommand(cmd);
        const opts = cmd.optsWithGlobals() as GlobalCliOptions & {
          query?: string;
          body?: string;
          text?: boolean;
          binary?: boolean;
        };

        const query = readJsonOrThrow(opts.query) as
          | Record<string, string | number | boolean | undefined>
          | undefined;
        const body = readJsonOrThrow(opts.body);

        const requestOptions: RequestOptions = {
          query,
          body,
        };

        if (opts.binary) {
          const data = await client.rawRequest<Uint8Array>(method, path, {
            ...requestOptions,
            responseType: 'binary',
          } as any);
          await writeOutput(data, cmd, { format: 'binary' });
        } else if (opts.text) {
          const data = await client.rawRequest<string>(method, path, {
            ...requestOptions,
            responseType: 'text',
          } as any);
          await writeOutput(data, cmd, { format: 'text' });
        } else {
          const data = await client.rawRequest<unknown>(method, path, {
            ...requestOptions,
            responseType: 'json',
          } as any);
          await writeOutput(data, cmd, { format: 'json' });
        }
      } catch (error) {
        handleCliError(error, { debug: isDebugEnabled(cmd) });
      }
    });

  try {
    await program.parseAsync(argv);
  } catch (error) {
    if (error instanceof CommanderError) {
      process.exitCode = error.exitCode;
      return;
    }
    throw error;
  }
}
