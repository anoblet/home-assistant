import assert from 'node:assert/strict';
import { test } from 'node:test';

import { loadConfigFromEnv } from './config.ts';

function withEnv(patch: Partial<Record<string, string | undefined>>, fn: () => void): void {
  const keys = Object.keys(patch);
  const previous: Record<string, string | undefined> = {};
  for (const key of keys) {
    previous[key] = process.env[key];
    const next = patch[key];
    if (next === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = next;
    }
  }

  try {
    fn();
  } finally {
    for (const key of keys) {
      const prev = previous[key];
      if (prev === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = prev;
      }
    }
  }
}

test('loadConfigFromEnv: missing token throws', () => {
  withEnv(
    {
      HOME_ASSISTANT_TOKEN: '',
      HOME_ASSISTANT_HOST: 'http://example.invalid',
      HOME_ASSISTANT_TIMEOUT_MS: '1000',
    },
    () => {
      assert.throws(() => loadConfigFromEnv(), {
        message: /HOME_ASSISTANT_TOKEN/i,
      });
    }
  );
});

test('loadConfigFromEnv: invalid HOME_ASSISTANT_TIMEOUT_MS falls back to default', () => {
  withEnv(
    {
      HOME_ASSISTANT_TOKEN: 'test-token',
      HOME_ASSISTANT_TIMEOUT_MS: 'nope',
    },
    () => {
      const cfg = loadConfigFromEnv();
      assert.equal(cfg.timeoutMs, 10000);
    }
  );
});

test("loadConfigFromEnv: HOME_ASSISTANT_TIMEOUT_MS with suffix (e.g. '5s') falls back to default", () => {
  withEnv(
    {
      HOME_ASSISTANT_TOKEN: 'test-token',
      HOME_ASSISTANT_TIMEOUT_MS: '5s',
    },
    () => {
      const cfg = loadConfigFromEnv();
      assert.equal(cfg.timeoutMs, 10000);
    }
  );
});

test('loadConfigFromEnv: non-positive HOME_ASSISTANT_TIMEOUT_MS falls back to default', () => {
  withEnv(
    {
      HOME_ASSISTANT_TOKEN: 'test-token',
      HOME_ASSISTANT_TIMEOUT_MS: '0',
    },
    () => {
      const cfg = loadConfigFromEnv();
      assert.equal(cfg.timeoutMs, 10000);
    }
  );
});

test('loadConfigFromEnv: valid HOME_ASSISTANT_TIMEOUT_MS is used', () => {
  withEnv(
    {
      HOME_ASSISTANT_TOKEN: 'test-token',
      HOME_ASSISTANT_TIMEOUT_MS: '12345',
    },
    () => {
      const cfg = loadConfigFromEnv();
      assert.equal(cfg.timeoutMs, 12345);
    }
  );
});
