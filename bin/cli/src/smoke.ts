import { pathToFileURL } from 'node:url';

import { createClientFromEnv } from './config.ts';

export async function main(): Promise<void> {
  try {
    const client = createClientFromEnv();

    const apiInfo = await client.getApiOverview();
    // eslint-disable-next-line no-console
    console.log('API overview:', apiInfo);

    const config = await client.getConfig();
    // eslint-disable-next-line no-console
    console.log('Config version:', config.version);

    const states = await client.getStates();
    // eslint-disable-next-line no-console
    console.log('Loaded entities:', states.length);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Smoke test failed:', error);
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  // eslint-disable-next-line unicorn/prefer-top-level-await
  main();
}
