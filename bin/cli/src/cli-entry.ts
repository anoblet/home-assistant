import { main } from './cli.ts';

function parseBooleanEnv(value: string | undefined): boolean {
  return value === '1' || value === 'true' || value === 'yes';
}

// eslint-disable-next-line unicorn/prefer-top-level-await
main().catch((error) => {
  const debug =
    parseBooleanEnv(process.env.HOME_ASSISTANT_DEBUG) || process.argv.includes('--debug');

  if (error instanceof Error) {
    // eslint-disable-next-line no-console
    console.error(error.message);
    if (debug && error.stack) {
      // eslint-disable-next-line no-console
      console.error(error.stack);
    }
  } else {
    // eslint-disable-next-line no-console
    console.error(String(error));
  }

  process.exitCode = 1;
});
