import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';

import { HttpClient } from './http.ts';

type FetchType = typeof fetch;

let originalFetch: FetchType | undefined;

afterEach(() => {
  if (originalFetch) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (globalThis as any).fetch = originalFetch;
    originalFetch = undefined;
  }
});

test('HttpClient: timeout abort maps to friendly error message', async () => {
  originalFetch = globalThis.fetch;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).fetch = (async (_url: string, init?: RequestInit) => {
    return await new Promise<Response>((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => {
        const err = new Error('Aborted');
        (err as { name?: string }).name = 'AbortError';
        reject(err);
      });
    });
  }) as unknown as FetchType;

  const client = new HttpClient({
    baseUrl: 'http://example.invalid',
    token: 't',
    timeoutMs: 5,
  });

  await assert.rejects(() => client.getJson('/api/'), {
    message: /Request timed out after 5ms/i,
  });
});

test('HttpClient: query params are encoded into the request URL', async () => {
  originalFetch = globalThis.fetch;

  let seenUrl: string | undefined;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).fetch = (async (url: string) => {
    seenUrl = url;
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as unknown as FetchType;

  const client = new HttpClient({
    baseUrl: 'http://example.invalid',
    token: 't',
    timeoutMs: 100,
  });

  await client.getJson('/api/template', {
    query: {
      q: 'a b',
      special: 'x&y',
    },
  });

  assert.ok(seenUrl);
  assert.match(seenUrl!, /q=a\+b|q=a%20b/);
  assert.match(seenUrl!, /special=x%26y/);
});

test('HttpClient: request path is trimmed (no leading whitespace surprises)', async () => {
  originalFetch = globalThis.fetch;

  let seenUrl: string | undefined;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).fetch = (async (url: string) => {
    seenUrl = url;
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as unknown as FetchType;

  const client = new HttpClient({
    baseUrl: 'http://example.invalid',
    token: 't',
    timeoutMs: 100,
  });

  await client.getJson('  /api/');

  assert.ok(seenUrl);
  assert.match(seenUrl!, /^http:\/\/example\.invalid\/api\//);
  assert.ok(!/%20/.test(seenUrl!));
});

test('HttpClient: absolute URLs are rejected before sending any request', async () => {
  originalFetch = globalThis.fetch;

  let callCount = 0;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).fetch = (async () => {
    callCount += 1;
    throw new Error('fetch should not be called');
  }) as unknown as FetchType;

  const client = new HttpClient({
    baseUrl: 'http://example.invalid',
    token: 't',
    timeoutMs: 100,
  });

  await assert.rejects(() => client.getJson('https://evil.invalid/api/config'), {
    message: /Absolute URLs are not allowed/i,
  });

  assert.equal(callCount, 0);
});
