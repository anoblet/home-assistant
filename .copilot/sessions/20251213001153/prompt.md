# Request
Research the most recent session in `.copilot/sessions`. Verify that the `vesync` custom component (`custom_components/vesync`) supports all features available for the Home Assistant **fan** (air purifier) and **humidifier** entity models. Research the `pyvesync` library and Home Assistant docs for best-practice implementation. Diagnose with Home Assistant logger + `ha core restart` and `ha core log` (no log file; must use CLI logs).

## Subagent execution note
You will be invoked with **only** the `sessionId`. First action: open this file at `.copilot/sessions/<sessionId>/prompt.md` and follow the instructions below, writing your results into the required output file(s).

## Constraints / notes
- Context7 docs lookup appears unavailable (unauthorized API key). Use local docs in repo + official web docs via `fetch_webpage` as fallback.
- Follow repo instructions: avoid grep at repo root; scope searches to `custom_components/vesync/**` and other specific folders.
- Use Home Assistant logger to enable debug for `custom_components.vesync` (and any underlying lib namespaces) while iterating.

## Deliverables
- A clear comparison of:
  - HA fan entity feature set vs what `custom_components/vesync` exposes for air purifiers
  - HA humidifier entity feature set vs what `custom_components/vesync` exposes for humidifiers
  - What `pyvesync` devices actually support
- Code changes in `custom_components/vesync` to close gaps.
- Iteration evidence: restart HA and inspect CLI logs after changes.

## Agent outputs
- Research agent: write findings to `.copilot/sessions/20251213001153/research.md`.
- Plan agent: write implementation plan to `.copilot/sessions/20251213001153/plan.md`.
- Implement agent: implement changes + write summary to `.copilot/sessions/20251213001153/implement.md`.
- Review agent: verify features and regressions + write to `.copilot/sessions/20251213001153/review.md`.
- Documentation agent: update any relevant docs/notes + write to `.copilot/sessions/20251213001153/documentation.md`.
- Feedback agent: concise final report to `.copilot/sessions/20251213001153/final.md`.
