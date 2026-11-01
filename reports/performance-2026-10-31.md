# Home Assistant instance performance diagnosis

> Current status, October 31 at approximately 20:00 EDT: resource pressure remains much lower after the fixes. Google metadata sync is now repaired: HTTP 200, with all 74 device IDs and names matching between Home Assistant and Google Homegraph. Earlier unresolved-sync findings below are historical and superseded by the continuation results.

Assessed October 31, 2026, approximately 18:17–18:22 America/New_York (EDT). Read-only runtime investigation; no services restarted, settings changed, or data purged.

## Finding

**The primary observed bottleneck is host-wide I/O and memory pressure with active paging.** This affects more than Home Assistant Core: Supervisor, local integrations, MQTT and media services show overlapping delays. There are also independent integration faults producing persistent failed work. The exact service or process generating the dominant disk reads remains unproven.

Platform: Raspberry Pi 4, aarch64, four CPUs, approximately 3.70 GiB RAM; Home Assistant OS 18.3 and Core 2026.10.4. Seventeen apps were running. These are measurements during a degraded period, not a long-term benchmark.

## Measured evidence

| Measurement | Observation | Interpretation |
| --- | --- | --- |
| Host load, initial 1/5/15 minute averages | 9.61 / 12.88 / 8.84 | Above four-core capacity; load includes tasks waiting on I/O, so this does not establish CPU saturation. |
| Host load, later | 22.05 / 16.91 / 10.79 | Contention worsened during collection. |
| Initial memory | 3,877,204 KiB total; 1,759,952 KiB available | Available memory alone hides ongoing reclaim/paging pressure. |
| Initial swap | 4,199,796 KiB used of 8,388,604 KiB | Includes compressed-memory mechanisms; do not equate this entire amount with disk-resident swap. Zswap reported 771,348 KiB compressed, representing 1,989,452 KiB. |
| Initial PSI, 60-second average | CPU some 28.52%; memory some/full 15.88% / 11.90%; I/O some/full 41.72% / 22.51% | Actual scheduler, reclaim and I/O stalls, beyond simple utilization. |
| Later PSI, 60-second average | CPU some 16.82%; memory some/full 48.86% / 39.88%; I/O some/full 80.98% / 59.58% | Severe shared resource stalls; these percentages overlap and must not be summed. |
| Bounded 10.021-second kernel counter delta | 14,877 swap pages in; 7,770 out; 11,908 major page faults | Paging was active, rather than only historical swap occupancy. |
| Same interval, whole `sda` device | 741.04 MiB read; 30.52 MiB written; 79.67% busy; mean read completion 11.03 ms | Strong read pressure. Mean completion includes queueing and is device-wide, not a database-specific latency. |
| Data volume | 95.3 GiB used; 16.6 GiB free; 85% utilization | Capacity concern, but not a demonstrated disk-full failure. |
| Kernel OOM counter | 0 | No OOM kill shown by this counter; this does not rule out memory pressure. |
| Direct Core HTTP GET `/`, one attempt | TCP connected in 4.7 ms; no first byte within 5.002 seconds; curl timeout, no status | Poor responsiveness on the direct internal Core path. A single unauthenticated root-page probe does not measure automation or browser rendering latency. |

PSI `some` means at least one task stalled; `full` measures simultaneous stalls of all non-idle tasks in the sampled scope. `/proc` exposed host-level counters from the SSH app; app resource statistics were collected separately through Supervisor.

Host journal corroboration: at 18:17:42 and 18:17:44 journald reported “Under memory pressure, flushing caches”; systemd-resolved reported the same at 18:17:59. Earlier container runtime operations logged deadline and stream-copy failures. These support shared contention; they do not identify a specific offending app.

## Service observations

Selected Supervisor snapshots (not synchronized samples or peak working-set measurements):

| Service | CPU reported | Memory reported |
| --- | ---: | ---: |
| Core | 2.56% | 514 MiB |
| Supervisor | 0.21% | 59 MiB |
| Advanced SSH & Web Terminal | 8.52% | 591 MiB |
| Grafana | 2.10% | 389 MiB |
| Music Assistant | 2.17% | 325 MiB |
| InfluxDB | 0.62% | 261 MiB |
| MariaDB | 0% | 87 MiB |
| AdGuard Home | 0% | 78 MiB |
| Whisper | 0% | 22 MiB |
| ESPHome Device Builder | 0% | 22 MiB |

Low sampled Core CPU does not establish that the host is healthy. Container memory counters omit swapped-out working sets and do not provide a full host accounting. The SSH app includes this investigation and other workspace processes; its observed usage cannot be treated as an idle baseline. Several lightweight voice/build services were idle at the sample, so blaming them individually is unsupported.

Direct Docker statistics were unavailable under the SSH app's protection mode. Protection was left enabled. Supervisor stats reported zero block-I/O counters, making them unsuitable for attributing the observed host disk traffic.

## Recurring faults and likely amplifiers

Counts below are warning/error records grouped by logger from the bounded `ha core logs -n 1500` result, covering 15:17:02–18:17:16 EDT. They are neither complete-day totals nor counts of unique incidents; go2rtc can replay older internal messages into a later warning.

1. **OpenWrt integration failure loop — confirmed fault, overhead unquantified.** `custom_components.openwrt_ubus.shared_data_manager` emitted 356 records and `extended_ubus` 190. Repeated system API permission-denied responses occurred around a 30-second cadence; unsupported temperature discovery warnings recurred too. Later network-device/iwinfo calls timed out and one response failed HTTP parsing. Correct the router RPC permissions and supported collectors, then verify successful poll cycles. Permission failures are distinct from the later broad timeout episode. LuCI device tracking also appears in slow entity updates; check whether both router integrations are needed before changing either.

2. **Google Assistant report-state requests repeatedly rejected — confirmed fault.** 380 records from `homeassistant.components.google_assistant.http`, with repeated HTTP 400 responses. This is failed outbound work and log churn, not evidence of a Google service outage. Inspect a redacted failing payload/response and exposed entity traits to identify the invalid report. Do not blindly retry or disable all reporting.

3. **Printer camera stream/recovery churn — confirmed fault, cause unresolved.** 86 go2rtc warning records and five camera-stream errors. Stream producer EOFs recur about every five seconds in replayed server logs; go2rtc repeatedly reports termination/unexpected stops around 18:10, 18:15 and 18:16. Termination alone does not establish an OOM kill. Check printer availability, live camera consumers and whether streams are unnecessarily kept open. Test on-demand streaming before changing camera configuration.

4. **Multiple integration timeouts — shared degradation plausible.** AdGuard updates exceed their 10-second schedule; kitchen AC exceeds its one-minute schedule; VeSync successful fetch duration grows from roughly 1.1 seconds to 20.2 and 26.8 seconds. Around 18:16, Core cannot reach Supervisor, many app-info requests time out, and MQTT reports no ACK within 10 seconds. Music Assistant also loses transport and Supervisor reports missing WebSocket PONGs. Host pressure makes a common local contributor plausible; router/LAN faults can coexist and were not excluded by this audit.

5. **Slow state updates across unrelated domains — symptoms, not proof of defective handlers.** Examples include MQTT hallway light 5.829 seconds, Spook entities/areas about 1.7–2.3 seconds, ESPHome sensors 0.4–0.8 seconds, and Adaptive Lighting 1.055 seconds. Profiling is needed to separate expensive callbacks from time lost to scheduling and paging. Do not disable lighting or presence behavior based solely on these warnings.

6. **Unavailable Z-Wave controller — independent availability issue.** The app is stopped; Supervisor repeatedly rejects its configured serial device because it does not exist. Core logged 17 Z-Wave warning/error records in the sample. Restore the intended controller path or retire unused integration configuration deliberately. WireGuard is also in an error state; its cause was not investigated.

## Configuration contributors to investigate

- `packages/shared/recorder.yaml` uses a secret-backed **MySQL** URL, a 60-second commit interval, 30-day retention, and exclusions for selected radar entities. The local 1.0 GiB `home-assistant_v2.db` is dated April 2022: its size is not evidence about the active recorder. Do not optimize or purge that file as a recorder fix.
- `packages/integrations/influxdb.yaml` defines an additional state export with three retries and no explicit include/exclude filter. This makes database fan-out and high-frequency telemetry plausible I/O contributors, but database size, retention, write throughput and slow queries were not measured. Recorder exclusions do not establish equivalent filtering in the separate InfluxDB configuration.
- `packages/shared/logger.yaml` enables debug for `custom_components.vesync` and `pyvesync`. Return them to normal verbosity when their diagnostic purpose is complete. This is a low-risk churn reduction, not a demonstrated cure for host paging.
- There are 358 package YAML files. File count and taxonomy are not evidence of steady-state runtime slowness; no package restructuring is recommended for performance.

## Recommended order of work

1. **Attribute disk reads and swapped working sets first.** Collect a short host/per-process I/O and swap sample through an existing supported host diagnostics path, alongside PSI, disk counters and app CPU/memory. Check scheduled backups, scans, image operations and database jobs during the same interval. Avoid expensive full-tree scans or database integrity checks while the host is stalled.
2. **Reduce or move the evidenced workload.** Once attribution is available, trial one nonessential workload at a time during an acceptable maintenance window. Grafana, history services, Music Assistant and workspace processes are candidates for review, not proven culprits. Record previous service state and rollback. Keep DNS, MQTT and household control dependencies running. If routine workload still causes paging, move heavy services to a host with more RAM and verify storage health/latency; this audit does not establish a defective disk or justify a specific purchase.
3. **Repair deterministic failures.** Address OpenWrt permissions/unsupported polls, invalid Google report-state payloads, Z-Wave device mapping and camera reconnect behavior. Verify successful operations, not just fewer log entries.
4. **Measure database demand before tuning retention.** Inspect active MariaDB and InfluxDB sizes, retention policies, high-volume entities and query/write latency using bounded read-only queries. Apply narrower telemetry filtering only where history requirements allow; preserve user-configurable settings and document rollback.
5. **Repeat comparable measurements.** Use the same direct Core read path for several bounded requests and repeat kernel counter/PSI samples under comparable load. Then check a read-only authenticated state request and actual dashboard responsiveness. Success means reduced sustained I/O/memory stalls, fewer major faults and timeouts, and responsive household controls. No before/after improvement is claimed because this was an audit.

## Scope and limitations

Sources: native `ha core/host info`, Core/Supervisor/app stats, app listing, bounded Core/Supervisor/host logs, `/proc/{loadavg,meminfo,vmstat,diskstats,pressure/*}`, filesystem capacity, relevant YAML and one direct Core HTTP probe. No credentials or raw logs are included here. No browser trace, event-loop profile, database query plan, SMART test, DNS/LAN benchmark, authenticated automation latency or per-process host I/O attribution was collected. The shared bottleneck is well evidenced; its precise workload ownership and the contribution of independent network faults remain open.

## Implementation follow-up — October 31, 2026

The user authorized implementation after the audit. Unrelated existing workspace
changes were preserved. The findings below supersede uncertainties in the initial
report where new evidence is available.

### Applied changes

- Removed the VeSync and pyvesync debug overrides from
  `packages/shared/logger.yaml`; they now inherit warning-level logging.
- Set the printer camera's `preload_stream` preference to false through the live
  camera WebSocket API. This preserves on-demand camera access. Updating the
  preference does not itself guarantee an already-running stream stops; Core
  restart is included in deployment.
- Disabled the Z-Wave integration entry through the supported config-entry API.
  Only the Sonoff Zigbee adapter is physically present; the saved HubZ Z-Wave
  controller path is absent. The Z-Wave app was already stopped, manual-start,
  and without a watchdog. No controller configuration, keys or entities were
  deleted. Re-enable the integration after restoring its intended hardware.
- Fixed OpenWrt file permissions with the narrow read-only ACL in
  `scripts/openwrt/home-assistant-monitoring.json`, deployed to the router's
  `/usr/share/rpcd/acl.d/`. Previously `system.info` and `system.board` succeeded
  while `file.read /proc/stat` and hwmon reads returned code 6. All three file
  reads succeeded after deployment. Live HA CPU and ath10k temperature sensors
  subsequently reported numeric values. Temperature is converted to the HA
  instance's Fahrenheit display unit.
- Changed router rpcd session timeout from 30 to 300 seconds and reloaded rpcd
  and the OpenWrt integration. The old lifetime collided with polling intervals
  and yielded stale-session access errors. Deployment and rollback instructions
  are beside the ACL file. Existing broad root permissions were not expanded
  beyond the listed read-only file paths.
- Replaced Google Assistant's reference to the rejected secret-backed private
  key with `!include ../../SERVICE_ACCOUNT.json`, an existing ignored credential
  for the same project and email. The old key failed Google's token endpoint
  with `invalid_grant: Invalid JWT Signature`. The existing alternative key
  authenticated successfully and completed a Homegraph device query with HTTP
  200. `report_state: true` is retained; no exposure lists were reduced.
- Stopped Grafana and set its start policy from automatic to manual, retaining
  its existing disabled watchdog. Grafana's data, dashboards and InfluxDB history
  remain intact. Start it with `ha apps start a0d7b954_grafana` when needed. This
  is an intentional availability tradeoff to free resources on the 4 GiB host.

### Additional attribution and database checks

An existing authorized host SSH connection on port 22222 allowed cgroup and
Docker diagnostics without changing SSH-app protection mode. Over approximately
20.7 seconds, Grafana read 322.5 MiB and held 418.9 MiB in RAM plus 187.3 MiB in
swap. Its logs showed internal dashboard/API timeouts. The SSH workspace app
read 373.6 MiB in the same interval and held 859.5 MiB in RAM plus 669.0 MiB in
swap. InfluxDB read 82.5 MiB; Core read 25.7 MiB. These are interval deltas;
cumulative Docker block-I/O totals were not treated as current throughput.

A further approximately 16.5-second process sample attributed 126.1 MiB of SSH
app reads to this active Codex process and 60.0 MiB to the VS Code extension host.
The active editor/agent session was preserved. This development workload shares
the host's limited memory and remains a contributor while work is running.

Read-only metadata checks found approximately 2,894.7 MiB in MariaDB `states`,
922.7 MiB in long-term `statistics`, 406.2 MiB in `state_attributes`, and 321.0 MiB
in `statistics_short_term`. Row counts are engine estimates. InfluxDB already
uses a 720-hour retention policy; its five Home Assistant shards totaled about
755 MiB and reported no write-point errors in the sampled counters. No retention
or history deletion was performed, and no speculative database tuning was applied.

### Rollback

Restore logger debug overrides only for a bounded diagnostic need. Set the
camera preference back to true to resume continuous preloading. Re-enable the
Z-Wave config entry only with the intended controller restored. Router rollback
is documented in `scripts/openwrt/README.md`. Restore Grafana automatic boot
through its app settings and start it to restore continuous availability. The
old Google private-key secrets remain untouched, but switching back to them
would restore the verified authentication failure.

Camera verification caveat: the installed Bambu integration implements
`is_streaming` as `available`, so the entity's `streaming` state does not prove
active video processing. After the first restart, the preference remained false,
there was no TCP connection to the printer's RTSP port in the host socket sample,
and no demux/go2rtc restart errors appeared in the new startup log. The camera
entity remained available for on-demand access.

The verified Google credential was discovered while the first restart was
already in progress. That running process still failed request-sync with the
old key. A further restart is necessary to load the final YAML credential
reference; a successful direct Google API probe alone is not deployment proof.

Final configuration validation: `ha core check` completed successfully against
the final Google credential include and logger configuration. Static validation
resolved all 66 include references across every Lovelace YAML file and the
changed integration package, including unregistered dashboard files. The ACL
JSON parses, repository whitespace checks pass, and the updated Home Assistant
skill passes its validator. `pnpm reload` was attempted: its initial assumed
success and a request made during startup were not accepted as deployment proof;
native Core restart and live runtime verification are used instead.

The credential include uses Home Assistant's documented service-account-file
configuration: [Google Assistant documentation](https://www.home-assistant.io/integrations/google_assistant/).

### Final live verification — approximately 18:42–18:44 EDT

Core reported `RUNNING` through its authenticated API after the final restart.
The OpenWrt and Bambu integrations loaded, while Z-Wave remained deliberately
disabled. Router CPU and temperature values updated across polling cycles.
Grafana's stopped/manual-start policy was read back from Supervisor.

| Comparable measurement | Audit sample | After changes |
| --- | --- | --- |
| Direct Core GET `/` | One attempt: no first byte within 5.002 s | Three HTTP 200 responses: total 596.94, 298.01 and 20.47 ms |
| Kernel interval | 10.021 s | 10.005 s |
| Swap pages read / written | 14,877 / 7,770 | 269 / 0 |
| Major page faults | 11,908 | 2,524 |
| Whole-disk read / write | 741.04 / 30.52 MiB | 278.80 / 4.30 MiB |
| Whole-disk busy time | 79.67% | 11.55% |
| Memory PSI some / full, 60 s | 48.86% / 39.88% | 2.75% / 2.34% |
| I/O PSI some / full, 60 s | 80.98% / 59.58% | 8.50% / 6.32% |
| Host 1 / 5 / 15 minute load | 22.05 / 16.91 / 10.79 | 2.01 / 3.32 / 5.96 |

These snapshots show recovery, not an isolated Grafana-only benchmark: Core was
restarted, multiple faults were corrected, cache state changed, and development
work continued. No percentile, steady-state guarantee or attribution of the
entire improvement to one change is claimed. The remaining reads and faults
show that resource contention has been reduced rather than eliminated.

During bounded Google HTTP debug logging, **five live state-report requests
received successful request-ID responses** between 18:42:10 and 18:43:18.
This verifies that the new key is active inside Home Assistant, beyond the
separate credential probe. Temporary debug logging was then reset to warning.
The final startup log had zero recurring router permission/system-fetch errors,
zero VeSync debug records, and zero camera demux/go2rtc restart errors at the
verification point. The RTSP socket sample showed no printer connection.

**Metadata-sync issue at 18:44, subsequently resolved in the continuation below:** request-sync for the actual linked
agent user still returns HTTP 400 `INVALID_ARGUMENT`, despite successful state
reporting. A default call made with the Supervisor identity returned 404; that
identity is not the linked Google user and was not used as evidence that the
real account is missing. The public fulfillment endpoint responds HTTP 405 to
GET, which establishes reachability but does not validate Google's authenticated
POST flow. Google Home account linking/project configuration and its fulfillment
logs need inspection to resolve metadata sync; this account-side state is not
available through the local API. See [Google's Request Sync documentation](https://developers.home.google.com/cloud-to-cloud/integration/request-sync).
Existing exposure lists and functional state reports were preserved.

Other remaining startup issues include unreachable ESPHome/Cast/Reolink devices,
a Wyze setup failure, Bambu cloud authorization, and legacy LuCI tracker ID
collisions. Their device credentials, hardware availability and registry history
were not changed speculatively. The active VS Code/Codex workload continues to
share the 4 GiB host; moving development or history/visualization workloads to
another machine remains the durable capacity option if pressure returns.

The installed `hass-cli` requires an API base URL ending in `/api`. The final
reload used `HASS_API_URL=http://172.30.32.1:8123/api pnpm reload`; earlier overrides
without that suffix produced 404 even with Core running. This corrected call
returned the client's assumed-success timeout message, so it is not counted as
an acknowledged reload. Final authenticated Core readback still reported
`RUNNING`, with no new targeted configuration/router/stream errors in the recent
log. The actual configuration deployment was verified through successful native
restarts and live Google state reports, router sensors and camera preferences.
The skill now records the required URL suffix. Temporary task-created credential
files were removed; the original credential stores were preserved.

## Continuation — October 31, approximately 19:51 EDT onward

The earlier “account-side” limitation on metadata sync was premature: the
existing CLI token belongs to the linked owner, so it can inspect the actual
Home Assistant SYNC response without creating a new Google agent user.
An authenticated local `action.devices.SYNC` returned HTTP 200 with 74 devices,
including **seven empty primary names**. The corresponding entities deliberately
use blank dashboard-friendly names and had no Google-specific name override.
Google requires a primary name in its [SYNC response schema](https://developers.home.google.com/cloud-to-cloud/intents/sync).

Added explicit Google names for Bathroom Door, Bathroom Lights, Bedroom Ceiling,
Hallway Lights, Kitchen Lights, Living Room Floor Lamp and Living Room Ceiling
in their existing area packages. Entity IDs, dashboard labels, device exposure
and traits are preserved. `ha core check` passed; all 65 Lovelace include targets
resolved. The required `pnpm reload` again returned its assumed-success timeout,
so a native Core restart deploys these startup-only Google YAML overrides.

A read-only attempt to obtain the project's Google Cloud error logs was denied
by the existing service account's log-view permissions. No IAM permissions,
Google project settings or account links were changed.

Before this continuation's restart, the resource improvements remained visible
more than an hour after the initial repairs. A 10.014-second sample at 19:53 EDT
recorded 45 swap pages read, zero written, 1,472 major faults, 125.57 MiB disk
reads and 12.58% disk busy time. Memory PSI some/full averaged 1.27%/1.00% over
60 seconds; I/O PSI was 3.70%/2.52%. Three direct Core requests completed in
871.89, 41.48 and 27.02 ms. These are additional snapshots, not percentiles.
The bounded recent log contained no new camera restart or recurring router
permission failures; remaining Google report-state 404s were limited to two
records at 18:45:26 in the inspected window.

### Continuation result — approximately 20:00 EDT

The native Core restart completed and its authenticated API reported `RUNNING`.
The owner-authenticated SYNC response still exposed the same 74 device IDs, now
with 74 nonempty primary names. A synchronous Homegraph `requestSync` then
returned **HTTP 200**. A subsequent read-only `devices.sync` returned 74 devices,
up from the previously stored 71, with **zero missing IDs and zero name
mismatches** against Home Assistant. This verifies actual cloud metadata
replacement, beyond a local configuration readback or queued acknowledgement.
No Google account relinking, permission changes, credential rotation or exposure
removal was needed for this second fault. The seven name overrides were the only
configuration changes in this continuation.

The initial report-state 404 at 19:56:54 occurred during startup before the
successful metadata sync; no newer Google failure was present in the bounded
verification log. Existing unrelated Wyze and device-availability startup issues
remain. The Home Assistant skill now documents owner-authenticated SYNC
inspection and Google-specific names for entities with blank dashboard labels;
its validator and whitespace checks passed.

Rollback for this continuation: remove the seven added `entity_config.name`
overrides from the six changed area packages and restart Core. That would
restore the malformed names and the demonstrated metadata-sync failure; it does
not alter the earlier resource or credential repairs.
