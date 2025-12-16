#!/usr/bin/env node

const path = require('node:path');
const { spawnSync } = require('node:child_process');

const entry = path.resolve(__dirname, '../src/cli-entry.ts');

const result = spawnSync(
  process.execPath,
  ['--no-warnings', '--experimental-strip-types', entry, ...process.argv.slice(2)],
  {
    stdio: 'inherit',
    env: {
      ...process.env,
      NODE_NO_WARNINGS: '1',
    },
  }
);

process.exitCode = result.status ?? 1;
