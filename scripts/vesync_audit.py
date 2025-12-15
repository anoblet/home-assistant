#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_expected_surface_from_coverage_doc(doc_path: Path) -> dict[str, Any]:
    """Extract the `vesync_expected_surface` JSON object from a markdown doc.

    The coverage doc is narrative; the fenced JSON block is the canonical, parseable source.
    """

    markdown = doc_path.read_text(encoding="utf-8")
    in_json_block = False
    buffer: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not in_json_block:
            if line == "```json":
                in_json_block = True
                buffer = []
            continue

        if line == "```":
            block = "\n".join(buffer).strip()
            in_json_block = False
            buffer = []
            if not block:
                continue
            try:
                parsed = json.loads(block)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict) and "vesync_expected_surface" in parsed:
                manifest = parsed.get("vesync_expected_surface")
                if not isinstance(manifest, dict):
                    raise ValueError("vesync_expected_surface must be a JSON object")
                return manifest
            continue

        buffer.append(raw_line)

    raise FileNotFoundError(
        f"No fenced JSON block with 'vesync_expected_surface' found in {doc_path}"
    )


def _sorted_str_set(values: Any) -> list[str]:
    if not values:
        return []
    return sorted({str(v) for v in values if v is not None and str(v).strip()})


def _set_diff(expected: set[str], actual: set[str]) -> dict[str, list[str]]:
    return {
        "missing": sorted(expected - actual),
        "extra": sorted(actual - expected),
    }


def _render_parity_markdown(report: dict[str, Any]) -> str:
    result = report.get("result") or {}
    ok = bool(result.get("ok"))

    lines: list[str] = []
    lines.append("# VeSync surface parity report")
    lines.append("")
    lines.append(f"- Result: {'PASS' if ok else 'FAIL'}")
    lines.append(f"- VeSync config entries (runtime): {result.get('runtime_entries', 0)}")
    lines.append(f"- Runtime entity domains observed: {', '.join(result.get('runtime_domains', [])) or 'n/a'}")
    lines.append("")

    def _section(title: str, diff_key: str) -> None:
        diff = report.get("diffs", {}).get(diff_key, {})
        missing = diff.get("missing") or []
        extra = diff.get("extra") or []
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"- Missing: {', '.join(missing) or 'none'}")
        lines.append(f"- Extra: {', '.join(extra) or 'none'}")
        lines.append("")

    _section("Platforms (code vs manifest)", "platforms")
    _section("Services (services.yaml vs manifest)", "services")

    runtime_diff = report.get("diffs", {}).get("runtime_domains", {})
    runtime_missing = runtime_diff.get("missing") or []
    runtime_extra = runtime_diff.get("extra") or []
    lines.append("## Runtime entity domains (runtime ⊆ manifest-supported)")
    lines.append("")
    lines.append(f"- Unexpected (FAIL if any): {', '.join(runtime_extra) or 'none'}")
    lines.append(f"- Supported but not observed (OK): {', '.join(runtime_missing) or 'none'}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _redact_title(title: Any) -> str | None:
    if title is None:
        return None
    if not isinstance(title, str):
        return str(title)

    # Config entry titles are often emails/usernames; treat as sensitive.
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", title):
        return "<redacted>"

    return title


def _find_vesync_config_entries(config_entries: dict[str, Any]) -> list[dict[str, Any]]:
    entries = config_entries.get("data", {}).get("entries", [])
    vesync_entries: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("domain") != "vesync":
            continue
        vesync_entries.append(
            {
                "entry_id": entry.get("entry_id"),
                "title": _redact_title(entry.get("title")),
                "state": entry.get("state"),
                "version": entry.get("version"),
                "minor_version": entry.get("minor_version"),
                "source": entry.get("source"),
            }
        )
    return vesync_entries


def _parse_platforms_from_init(repo_root: Path) -> list[str]:
    init_py = repo_root / "custom_components" / "vesync" / "__init__.py"
    if not init_py.exists():
        return []

    text = init_py.read_text(encoding="utf-8")
    raw = set(re.findall(r"Platform\.([A-Z_]+)", text))
    return sorted({p.lower() for p in raw})


def _parse_services_from_services_yaml(repo_root: Path) -> list[str]:
    services_yaml = repo_root / "custom_components" / "vesync" / "services.yaml"
    if not services_yaml.exists():
        return []

    service_names: list[str] = []
    for line in services_yaml.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        if line[0].isspace():
            continue
        if not line.endswith(":"):
            continue
        key = line[:-1].strip()
        if not key:
            continue
        service_names.append(key)

    return sorted(set(service_names))


def _devices_for_entry(device_registry: dict[str, Any], entry_id: str) -> list[dict[str, Any]]:
    devices = device_registry.get("data", {}).get("devices", [])
    result: list[dict[str, Any]] = []
    for dev in devices:
        if entry_id not in (dev.get("config_entries") or []):
            continue
        identifiers = dev.get("identifiers") or []
        vesync_identifiers = [iden[1] for iden in identifiers if iden and iden[0] == "vesync"]

        result.append(
            {
                "device_id": dev.get("id"),
                "name": dev.get("name"),
                "name_by_user": dev.get("name_by_user"),
                "model": dev.get("model"),
                "manufacturer": dev.get("manufacturer"),
                "sw_version": dev.get("sw_version"),
                "hw_version": dev.get("hw_version"),
                "vesync_identifiers": vesync_identifiers,
            }
        )

    return result


def _entities_for_entry(entity_registry: dict[str, Any], entry_id: str) -> list[dict[str, Any]]:
    entities = entity_registry.get("data", {}).get("entities", [])
    result: list[dict[str, Any]] = []
    for ent in entities:
        if ent.get("config_entry_id") != entry_id:
            continue
        entity_id = ent.get("entity_id")
        domain = None
        if isinstance(entity_id, str) and "." in entity_id:
            domain = entity_id.split(".", 1)[0]
        result.append(
            {
                "domain": domain,
                "entity_id": entity_id,
                "unique_id": ent.get("unique_id"),
                "platform": ent.get("platform"),
                "device_id": ent.get("device_id"),
                "entity_category": ent.get("entity_category"),
                "disabled_by": ent.get("disabled_by"),
                "hidden_by": ent.get("hidden_by"),
                "original_name": ent.get("original_name"),
                "original_device_class": ent.get("original_device_class"),
            }
        )
    return result


def _render_markdown_report(inventory: dict[str, Any]) -> str:
    lines: list[str] = []

    def _short(value: Any) -> str:
        if value is None:
            return "n/a"
        text = str(value)
        if len(text) <= 12:
            return text
        return f"{text[:6]}…{text[-4:]}"

    lines.append("# VeSync surface / runtime inventory")
    lines.append("")

    entries = inventory.get("vesync", {}).get("config_entries", [])
    lines.append(f"- VeSync config entries: {len(entries)}")
    lines.append(f"- Platforms (from code): {', '.join(inventory.get('integration', {}).get('platforms', [])) or 'n/a'}")
    lines.append(f"- Services (from services.yaml): {', '.join(inventory.get('integration', {}).get('services', [])) or 'n/a'}")
    lines.append("")

    for entry in entries:
        entry_id = entry.get("entry_id")
        devices = entry.get("devices", [])
        entities = entry.get("entities", [])

        lines.append(f"## Config entry: {entry.get('title') or 'VeSync'}")
        lines.append("")
        lines.append(f"- entry_id: {_short(entry_id)}")
        lines.append(f"- state: {entry.get('state')}")
        lines.append(f"- version: {entry.get('version')} (minor: {entry.get('minor_version')})")
        lines.append(f"- devices: {len(devices)}")
        lines.append(f"- entities: {len(entities)}")
        lines.append("")

        by_platform: dict[str, int] = defaultdict(int)
        for ent in entities:
            by_platform[str(ent.get("domain") or "unknown")] += 1

        if by_platform:
            platform_bits = ", ".join(
                f"{platform}={count}" for platform, count in sorted(by_platform.items())
            )
            lines.append(f"Entities by domain: {platform_bits}")
            lines.append("")

        if devices:
            lines.append("Devices:")
            for dev in sorted(devices, key=lambda d: str(d.get("name") or "")):
                lines.append(
                    f"- {dev.get('name') or 'Unnamed'} (device_id={_short(dev.get('device_id'))})"
                )
            lines.append("")

        if entities:
            lines.append("Entities:")
            for ent in sorted(entities, key=lambda e: str(e.get("entity_id") or "")):
                lines.append(
                    f"- {ent.get('entity_id')} (platform={ent.get('platform')}, unique_id={_short(ent.get('unique_id'))})"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a VeSync runtime inventory from Home Assistant .storage registries."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (defaults to current working directory).",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=None,
        help="Home Assistant .storage directory (defaults to <repo-root>/.storage).",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Write inventory JSON to this path.",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Write a markdown report to this path.",
    )

    parser.add_argument(
        "--coverage-doc",
        type=Path,
        default=None,
        help=(
            "Path to docs/custom-components/vesync-pyvesync-coverage.md (defaults to <repo-root>/docs/custom-components/vesync-pyvesync-coverage.md)."
        ),
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare code/runtime surface against the coverage doc manifest and exit non-zero on mismatch.",
    )
    parser.add_argument(
        "--out-compare-json",
        type=Path,
        default=None,
        help="Write the parity comparison JSON report to this path.",
    )
    parser.add_argument(
        "--out-compare-md",
        type=Path,
        default=None,
        help="Write the parity comparison markdown report to this path.",
    )

    args = parser.parse_args()

    repo_root: Path = args.repo_root
    storage_dir: Path = args.storage_dir or (repo_root / ".storage")

    config_entries_path = storage_dir / "core.config_entries"
    entity_registry_path = storage_dir / "core.entity_registry"
    device_registry_path = storage_dir / "core.device_registry"

    for required in (config_entries_path, entity_registry_path, device_registry_path):
        if not required.exists():
            raise SystemExit(f"Missing required file: {required}")

    config_entries = _read_json(config_entries_path)
    entity_registry = _read_json(entity_registry_path)
    device_registry = _read_json(device_registry_path)

    vesync_entries = _find_vesync_config_entries(config_entries)

    inventory: dict[str, Any] = {
        "integration": {
            "platforms": _parse_platforms_from_init(repo_root),
            "services": _parse_services_from_services_yaml(repo_root),
        },
        "runtime": {},
        "vesync": {
            "config_entries": [],
        },
    }

    for entry in vesync_entries:
        entry_id = entry.get("entry_id")
        if not entry_id:
            continue

        devices = _devices_for_entry(device_registry, entry_id)
        entities = _entities_for_entry(entity_registry, entry_id)

        inventory["vesync"]["config_entries"].append(
            {
                **entry,
                "devices": devices,
                "entities": entities,
            }
        )

    runtime_domains_all: set[str] = set()
    for entry in inventory["vesync"]["config_entries"]:
        domains = _sorted_str_set(e.get("domain") for e in (entry.get("entities") or []))
        entry["entity_domains"] = domains
        runtime_domains_all.update(domains)

    inventory["runtime"]["entity_domains"] = sorted(runtime_domains_all)

    if args.compare:
        coverage_doc = args.coverage_doc or (
            repo_root / "docs" / "custom-components" / "vesync-pyvesync-coverage.md"
        )
        manifest = _extract_expected_surface_from_coverage_doc(coverage_doc)

        expected_platforms = set(_sorted_str_set(manifest.get("platforms")))
        expected_services = set(_sorted_str_set(manifest.get("services")))

        supported_runtime_domains: set[str] = set()
        device_classes = manifest.get("device_classes") or {}
        if isinstance(device_classes, dict):
            for _cls, spec in device_classes.items():
                if isinstance(spec, dict):
                    supported_runtime_domains.update(_sorted_str_set(spec.get("platforms")))
        firmware = manifest.get("firmware")
        if isinstance(firmware, dict):
            supported_runtime_domains.update(_sorted_str_set(firmware.get("platforms")))

        observed_platforms = set(_sorted_str_set(inventory.get("integration", {}).get("platforms")))
        observed_services = set(_sorted_str_set(inventory.get("integration", {}).get("services")))
        observed_runtime_domains = set(_sorted_str_set(inventory.get("runtime", {}).get("entity_domains")))

        diffs = {
            "platforms": _set_diff(expected_platforms, observed_platforms),
            "services": _set_diff(expected_services, observed_services),
            # Runtime domains depend on which device families exist in this instance.
            # Treat as: observed ⊆ supported.
            "runtime_domains": {
                "missing": sorted(supported_runtime_domains - observed_runtime_domains),
                "extra": sorted(observed_runtime_domains - supported_runtime_domains),
            },
        }

        ok = (
            not diffs["platforms"]["missing"]
            and not diffs["platforms"]["extra"]
            and not diffs["services"]["missing"]
            and not diffs["services"]["extra"]
            and not diffs["runtime_domains"]["extra"]
        )

        parity_report: dict[str, Any] = {
            "result": {
                "ok": ok,
                "runtime_entries": len(inventory["vesync"]["config_entries"]),
                "runtime_domains": sorted(observed_runtime_domains),
            },
            "expected": {
                "platforms": sorted(expected_platforms),
                "services": sorted(expected_services),
                "runtime_domains_supported": sorted(supported_runtime_domains),
            },
            "observed": {
                "platforms": sorted(observed_platforms),
                "services": sorted(observed_services),
                "runtime_domains": sorted(observed_runtime_domains),
            },
            "diffs": diffs,
        }

        print(f"VeSync parity: {'PASS' if ok else 'FAIL'}")
        if not ok:
            platforms = diffs.get("platforms", {})
            services = diffs.get("services", {})
            runtime = diffs.get("runtime_domains", {})

            print(
                "Platforms missing:",
                ", ".join(platforms.get("missing") or []) or "none",
            )
            print(
                "Platforms extra:",
                ", ".join(platforms.get("extra") or []) or "none",
            )
            print(
                "Services missing:",
                ", ".join(services.get("missing") or []) or "none",
            )
            print(
                "Services extra:",
                ", ".join(services.get("extra") or []) or "none",
            )
            print(
                "Runtime domains unexpected:",
                ", ".join(runtime.get("extra") or []) or "none",
            )

        if args.out_compare_json:
            args.out_compare_json.parent.mkdir(parents=True, exist_ok=True)
            args.out_compare_json.write_text(
                json.dumps(parity_report, indent=2, sort_keys=True), encoding="utf-8"
            )

        if args.out_compare_md:
            args.out_compare_md.parent.mkdir(parents=True, exist_ok=True)
            args.out_compare_md.write_text(_render_parity_markdown(parity_report), encoding="utf-8")

        if not ok:
            return 2

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8"
        )

    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(_render_markdown_report(inventory), encoding="utf-8")

    # Human-readable summary for terminal use.
    total_entries = len(inventory["vesync"]["config_entries"])
    total_entities = sum(
        len(e.get("entities", [])) for e in inventory["vesync"]["config_entries"]
    )
    total_devices = sum(
        len(e.get("devices", [])) for e in inventory["vesync"]["config_entries"]
    )
    print(f"VeSync entries: {total_entries}; devices: {total_devices}; entities: {total_entities}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
