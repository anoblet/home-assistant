import assert from 'node:assert/strict';
import { test } from 'node:test';

import { main } from './cli.ts';

async function captureIo(fn: () => Promise<void> | void): Promise<{
  stdout: string;
  stderr: string;
  exitCode: number | undefined;
}> {
  const stdoutChunks: string[] = [];
  const stderrChunks: string[] = [];

  const originalStdoutWrite = process.stdout.write.bind(process.stdout);
  const originalStderrWrite = process.stderr.write.bind(process.stderr);
  const originalExitCode = process.exitCode;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (process.stdout as any).write = (chunk: any) => {
    stdoutChunks.push(Buffer.isBuffer(chunk) ? chunk.toString('utf8') : String(chunk));
    return true;
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (process.stderr as any).write = (chunk: any) => {
    stderrChunks.push(Buffer.isBuffer(chunk) ? chunk.toString('utf8') : String(chunk));
    return true;
  };

  process.exitCode = undefined;

  try {
    await fn();
  } finally {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (process.stdout as any).write = originalStdoutWrite;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (process.stderr as any).write = originalStderrWrite;
  }

  const exitCode = process.exitCode;
  process.exitCode = originalExitCode;

  return {
    stdout: stdoutChunks.join(''),
    stderr: stderrChunks.join(''),
    exitCode,
  };
}

test('main: --help exits cleanly without throwing', async () => {
  const result = await captureIo(async () => {
    await main(['node', 'cli.js', '--help']);
  });

  assert.equal(result.exitCode ?? 0, 0);
  assert.match(result.stdout, /Home Assistant REST API CLI/i);
});

test('main: invalid --timeout fails fast as usage error', async () => {
  const result = await captureIo(async () => {
    await main(['node', 'cli.js', '--timeout', 'nope', 'api', 'info']);
  });

  assert.ok((result.exitCode ?? 0) !== 0);
  assert.match(result.stderr, /timeout/i);
});

test("main: --timeout does not accept suffixes like '5s'", async () => {
  const result = await captureIo(async () => {
    await main(['node', 'cli.js', '--timeout', '5s', 'api', 'info']);
  });

  assert.ok((result.exitCode ?? 0) !== 0);
  assert.match(result.stderr, /timeout/i);
});

test('main: JSON parse errors do not show a stack by default', async () => {
  const result = await captureIo(async () => {
    await main([
      'node',
      'cli.js',
      '--token',
      'test-token',
      'events',
      'fire',
      'test_event',
      '--data',
      '{',
    ]);
  });

  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /Failed to parse JSON/i);
  assert.ok(!/\n\s*at\s+/i.test(result.stderr));
});

test('main: JSON parse errors include a stack when debug is enabled', async () => {
  const result = await captureIo(async () => {
    await main([
      'node',
      'cli.js',
      '--debug',
      '--token',
      'test-token',
      'events',
      'fire',
      'test_event',
      '--data',
      '{',
    ]);
  });

  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /Failed to parse JSON/i);
  assert.match(result.stderr, /\n\s*at\s+/i);
});
