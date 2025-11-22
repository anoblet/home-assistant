"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.main = main;
const config_1 = require("./config");
async function main() {
    try {
        const client = (0, config_1.createClientFromEnv)();
        const apiInfo = await client.getApiOverview();
        // eslint-disable-next-line no-console
        console.log('API overview:', apiInfo);
        const config = await client.getConfig();
        // eslint-disable-next-line no-console
        console.log('Config version:', config.version);
        const states = await client.getStates();
        // eslint-disable-next-line no-console
        console.log('Loaded entities:', states.length);
    }
    catch (error) {
        // eslint-disable-next-line no-console
        console.error('Smoke test failed:', error);
        process.exitCode = 1;
    }
}
if (require.main === module) {
    // eslint-disable-next-line unicorn/prefer-top-level-await
    main();
}
