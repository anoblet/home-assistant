---
name: error
---

# Error Prompt

## Instructions

1. Run `ha core logs`
2. Check for any error messages or warnings related to `includes` and `packages`.
3. If any are found, investigate and fix the specific files mentioned in those directories.
4. After making changes, run `ha core restart` and re-check the logs for any remaining warnings or errors related to `includes` and `packages`.
5. Repeat this process until there are no remaining warnings or errors related to `includes` and `packages` in the logs.

Notes:

- If there are errors or issues that are not able to be fixed by modifying files in `includes` and `packages`, document those issues and any relevant error messages in a new file called `tmp/error-investigation.md` for further analysis.
- Use reasonable default values when entity values are unavailable
