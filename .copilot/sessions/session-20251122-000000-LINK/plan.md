# Plan

## Goal

Implement the `link` package to create relative symlinks based on a JSON configuration file.

## Steps

1.  **Implement `copilot/packages/link/src/index.ts`**:
    - Use `fs` and `path` modules.
    - Read the JSON file provided as a command-line argument.
    - Recursively traverse the JSON structure.
    - Create directories as needed.
    - Create symlinks using the relative paths provided in the JSON.
    - Handle existing files/links (overwrite).
2.  **Verify `package.json`**:
    - Ensure the `link` script is correctly defined as `"link": "tsx copilot/packages/link/src/index.ts"`.
3.  **Test**:
    - Create a dummy `test_link.json`.
    - Run `pnpm link test_link.json`.
    - Verify links are created.
    - Clean up.

## JSON Structure Logic

- Root keys are directories relative to CWD.
- Nested keys append to the directory path.
- Array values contain source paths (relative to the current nested directory).
- Link name is the basename of the source path.
