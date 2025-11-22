# Review

## Verification

- [x] `copilot/packages/link/src/index.ts` implemented.
- [x] Script logic handles JSON parsing, directory creation, and symlinking.
- [x] Recursive structure support verified by logic inspection (and simple test case covered the basic flow).
- [x] `package.json` has the `link` script.
- [x] Tested with `test_link.json` and verified symlink creation and content.

## Notes

- The script uses `fs.symlinkSync` which works for files and directories.
- It overwrites existing links/files at the destination.
- It creates parent directories if they don't exist.
