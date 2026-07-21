r"""Audit the archived Robot Harness prediction bundle without copying raw JSONL.

The June 2026 extraction contains paths longer than the legacy Windows
``MAX_PATH`` limit.  This tool prefixes local paths with ``\\?\`` on Windows,
streams every expected prediction file, and emits a lightweight manifest with
content hashes, row/schema checks, and four-model common-support fingerprints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
from pathlib import Path
from typing import Any, Iterable


D_SUITES = [
    "sft_tool_call_holdout",
    "project_robot_sandbox_eval",
    "safety_side_effect_eval",
    "browser_deferred_eval",
    "cross_source_generalization_eval",
]

OOD_SUITES = [
    "appworld_ood_api_policy_probe",
    "toolace_schema_given_probe",
    "toolace_schema_absent_probe",
    "quarantine_safety_probe",
    "robovlm_point_general_probe",
]

RUN_DIRS = {
    "base32": {
        "D": "eval/native_tools_v1/results/native_qwen3vl_32b_schemaaware_full_20260617_2114",
        "OOD": "eval/ood_probe_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_ood_base32",
    },
    "sft32": {
        "D": "eval/native_tools_v1/results/native_tool_restraint_32b_sft_20260618_114113",
        "OOD": "eval/ood_probe_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_ood_sft32",
    },
    "grpo100": {
        "D": "eval/native_tools_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_d_grpo32b_ckpt100",
        "OOD": "eval/ood_probe_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_ood_grpo32b_ckpt100",
    },
    "grpo200": {
        "D": "eval/native_tools_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_d_grpo32b_ckpt200",
        "OOD": "eval/ood_probe_v1/results/eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_ood_grpo32b_ckpt200",
    },
}

REMOTE_ROOT = "/data/msz/dataset/online_agent/training_pipeline_v2_language_full"

MISSING_SLOT_MODELS = {
    "sft_tool_call_holdout": {"base32", "sft32"},
    "cross_source_generalization_eval": {"base32", "sft32"},
    "toolace_schema_given_probe": {"base32", "sft32", "grpo100", "grpo200"},
    "toolace_schema_absent_probe": {"base32", "sft32", "grpo100", "grpo200"},
}


def extended_path(path: Path) -> str:
    """Return a path suitable for long-path-aware Windows file APIs."""

    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


def file_exists(path: Path) -> bool:
    return os.path.isfile(extended_path(path))


def plain_path(path: str) -> Path:
    """Remove an extended-length prefix returned by ``os.walk``."""

    if path.startswith("\\\\?\\UNC\\"):
        return Path("\\\\" + path[8:])
    if path.startswith("\\\\?\\"):
        return Path(path[4:])
    return Path(path)


def file_identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with open(extended_path(path), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"bytes": size, "sha256": digest.hexdigest().upper()}


def read_json(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    identity = file_identity(path)
    with open(extended_path(path), "r", encoding="utf-8") as stream:
        return json.load(stream), identity


def ordered_id_digest(ids: Iterable[str]) -> str:
    """Hash a collision-resistant length-prefixed ordered ID stream."""

    digest = hashlib.sha256()
    for item in ids:
        encoded = item.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest().upper()


def inspect_jsonl(path: Path) -> tuple[dict[str, Any], list[str]]:
    content_hash = hashlib.sha256()
    ids: list[str] = []
    fields: set[str] = set()
    metric_fields: set[str] = set()
    bytes_seen = 0
    rows = 0
    bad_json = 0
    missing_id = 0
    empty_output = 0

    with open(extended_path(path), "rb") as stream:
        for raw in stream:
            content_hash.update(raw)
            bytes_seen += len(raw)
            if not raw.strip():
                continue
            rows += 1
            try:
                row = json.loads(raw)
            except (TypeError, json.JSONDecodeError):
                bad_json += 1
                continue
            fields.update(row)
            metrics = row.get("metrics")
            if isinstance(metrics, dict):
                metric_fields.update(metrics)
            identifier = row.get("id")
            if identifier is None or str(identifier) == "":
                missing_id += 1
            else:
                ids.append(str(identifier))
            output = row.get("output")
            if output is None or (isinstance(output, str) and not output.strip()):
                empty_output += 1

    unique_ids = len(set(ids))
    result = {
        "bytes": bytes_seen,
        "sha256": content_hash.hexdigest().upper(),
        "rows": rows,
        "unique_ids": unique_ids,
        "duplicate_ids": len(ids) - unique_ids,
        "missing_id": missing_id,
        "empty_output": empty_output,
        "bad_json": bad_json,
        "ordered_id_sha256": ordered_id_digest(ids),
        "fields": sorted(fields),
        "metrics_fields": sorted(metric_fields),
    }
    return result, ids


def normalize_model(model_key: str, model_path: str) -> str:
    combined = f"{model_key} {model_path}".lower()
    if "checkpoint-100" in combined or "ckpt100" in combined:
        return "grpo100"
    if "checkpoint-200" in combined or "ckpt200" in combined:
        return "grpo200"
    if "sft_tool_restraint_32b" in combined or "sft32" in combined:
        return "sft32"
    if "32b-instruct" in combined or "base_32b" in combined or "base32" in combined:
        return "base32"
    if "8b-instruct" in combined or "base_8b" in combined or "base8" in combined:
        return "base8"
    return "unknown"


def recovery_source_path(split: str, suite: str, metrics: dict[str, Any]) -> str:
    recorded = str(metrics.get("data") or metrics.get("data_path") or "")
    if recorded.startswith("/"):
        return recorded
    if recorded:
        return f"{REMOTE_ROOT}/{recorded.lstrip('/')}"
    if split == "OOD":
        return f"{REMOTE_ROOT}/eval/ood_probe_v1/suites/{suite}.jsonl"
    return f"{REMOTE_ROOT}/eval/suites/{suite}.jsonl"


def localize_remote_path(root: Path, remote_path: str) -> Path | None:
    prefix = REMOTE_ROOT.rstrip("/") + "/"
    if not remote_path.startswith(prefix):
        return None
    return root / remote_path[len(prefix) :]


def build_recovery_slots(
    root: Path, records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for record in records:
        if record["exists"]:
            continue
        model = record["model"]
        split = record["split"]
        suite = record["suite"]
        run_dir = root / RUN_DIRS[model][split]
        metrics_path = run_dir / f"{suite}.metrics.json"
        run_manifest_path = run_dir / "run_manifest.json"
        launch_manifest_path = run_dir / "launch_manifest.json"
        metrics, metrics_identity = read_json(metrics_path)
        run_manifest, run_identity = read_json(run_manifest_path)
        launch_manifest: dict[str, Any] = {}
        launch_identity: dict[str, Any] | None = None
        if file_exists(launch_manifest_path):
            launch_manifest, launch_identity = read_json(launch_manifest_path)

        output_root = str(launch_manifest.get("output_root") or "")
        if not output_root:
            output_root = f"{REMOTE_ROOT}/{RUN_DIRS[model][split]}"
        source_path = recovery_source_path(split, suite, metrics)
        localized_source = localize_remote_path(root, source_path)
        metrics_values = metrics.get("metrics") or {}
        slot = {
            "split": split,
            "suite": suite,
            "model": model,
            "expected_relative_path": record["relative_path"],
            "expected_remote_path": f"{output_root.rstrip('/')}/{suite}.predictions.jsonl",
            "source_suite_remote_path": source_path,
            "source_suite_local_exists": bool(
                localized_source and file_exists(localized_source)
            ),
            "expected_rows_from_metrics": metrics_values.get("n"),
            "metrics_relative_path": metrics_path.relative_to(root).as_posix(),
            "metrics_sha256": metrics_identity["sha256"],
            "metrics_bytes": metrics_identity["bytes"],
            "metrics_generated_at": metrics.get("generated_at"),
            "scoring_version": metrics.get("scoring_version"),
            "embedding_backend": metrics.get("embedding_backend"),
            "rescored_from_predictions": metrics.get("rescored_from_predictions"),
            "run_manifest_relative_path": run_manifest_path.relative_to(root).as_posix(),
            "run_manifest_sha256": run_identity["sha256"],
            "run_manifest_bytes": run_identity["bytes"],
            "run_id": run_manifest.get("run_id"),
            "model_key": run_manifest.get("model_key"),
            "model_path": run_manifest.get("model_path"),
            "max_samples": run_manifest.get("max_samples"),
            "max_new_tokens": run_manifest.get("max_new_tokens"),
            "max_seq_length": run_manifest.get("max_seq_length"),
        }
        if launch_identity:
            slot.update(
                {
                    "launch_manifest_relative_path": launch_manifest_path.relative_to(
                        root
                    ).as_posix(),
                    "launch_manifest_sha256": launch_identity["sha256"],
                    "launch_manifest_bytes": launch_identity["bytes"],
                }
            )
        slots.append(slot)
    return slots


def scan_recovery_candidates(
    root: Path,
    search_roots: list[Path],
    recovery_slots: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    target_names = {f"{suite}.predictions.jsonl" for suite in MISSING_SLOT_MODELS}
    expected_rows = {
        (slot["suite"], slot["model"]): slot["expected_rows_from_metrics"]
        for slot in recovery_slots
    }
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    hits_by_root: dict[str, int] = {}

    for search_root in search_roots:
        root_hits = 0
        for dir_path, _dir_names, file_names in os.walk(extended_path(search_root)):
            for filename in sorted(set(file_names) & target_names):
                path = plain_path(dir_path) / filename
                key = str(path.resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                root_hits += 1
                run_dir = path.parent
                manifest_path = run_dir / "run_manifest.json"
                if not file_exists(manifest_path):
                    manifest_path = run_dir / "launch_manifest.json"
                manifest: dict[str, Any] = {}
                manifest_identity: dict[str, Any] | None = None
                if file_exists(manifest_path):
                    manifest, manifest_identity = read_json(manifest_path)
                inspection, _ids = inspect_jsonl(path)
                suite = filename[: -len(".predictions.jsonl")]
                normalized_model = normalize_model(
                    str(manifest.get("model_key") or ""),
                    str(manifest.get("model_path") or ""),
                )
                reasons: list[str] = []
                if normalized_model not in MISSING_SLOT_MODELS[suite]:
                    reasons.append("model_not_missing_for_suite")
                required_rows = expected_rows.get((suite, normalized_model))
                if required_rows is not None and inspection["rows"] != required_rows:
                    reasons.append("row_count_mismatch")
                if normalized_model in {"base8", "unknown"}:
                    reasons.append("model_identity_mismatch")
                verdict = "manual_identity_candidate" if not reasons else "REJECT"
                try:
                    display_path = path.relative_to(root).as_posix()
                    path_scope = "extraction-relative"
                except ValueError:
                    display_path = str(path.resolve())
                    path_scope = "absolute"
                candidate = {
                    "suite": suite,
                    "relative_or_absolute_path": display_path,
                    "path_scope": path_scope,
                    "run_dir_name": run_dir.name,
                    "normalized_model": normalized_model,
                    "model_key": manifest.get("model_key"),
                    "model_path": manifest.get("model_path"),
                    "max_samples": manifest.get("max_samples"),
                    "batch_size": manifest.get("batch_size"),
                    "max_new_tokens": manifest.get("max_new_tokens"),
                    "scoring_version": manifest.get("scoring_version"),
                    "rows": inspection["rows"],
                    "sha256": inspection["sha256"],
                    "ordered_id_sha256": inspection["ordered_id_sha256"],
                    "verdict": verdict,
                    "rejection_reasons": reasons,
                }
                if manifest_identity:
                    candidate["manifest_sha256"] = manifest_identity["sha256"]
                candidates.append(candidate)
        hits_by_root[str(search_root.resolve())] = root_hits
    candidates.sort(
        key=lambda item: (
            item["suite"],
            item["normalized_model"],
            item["run_dir_name"],
        )
    )
    return candidates, hits_by_root


def inspect_archive(
    archive: Path | None, recovery_slots: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if archive is None:
        return None
    identity = file_identity(archive)
    targets = {f"{suite}.predictions.jsonl" for suite in MISSING_SLOT_MODELS}
    exact_missing = {
        "training_pipeline_v2_language_full/" + slot["expected_relative_path"]
        for slot in recovery_slots
    }
    with tarfile.open(extended_path(archive), "r:gz") as bundle:
        names = [member.name for member in bundle.getmembers() if member.isfile()]
    matching = sorted(
        name for name in names if Path(name).name in targets
    )
    exact = sorted(set(matching) & exact_missing)
    return {
        "path": str(archive.resolve()),
        "sha256": identity["sha256"],
        "bytes": identity["bytes"],
        "members": len(names),
        "matching_candidate_members": len(matching),
        "exact_missing_target_members": len(exact),
        "exact_missing_target_paths": exact,
    }


def build_manifest(
    root: Path,
    evidence_date: str,
    search_roots: list[Path],
    archive: Path | None,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    ids_by_suite_model: dict[tuple[str, str], list[str]] = {}

    for split, suites in (("D", D_SUITES), ("OOD", OOD_SUITES)):
        for suite in suites:
            for model, split_dirs in RUN_DIRS.items():
                run_dir = root / split_dirs[split]
                primary = run_dir / f"{suite}.predictions.jsonl"
                record: dict[str, Any] = {
                    "split": split,
                    "suite": suite,
                    "model": model,
                    "relative_path": primary.relative_to(root).as_posix(),
                    "exists": file_exists(primary),
                    "schema_aware_exists": file_exists(
                        run_dir / f"{suite}.schema_aware.predictions.jsonl"
                    ),
                    "ood_scored_exists": file_exists(
                        run_dir / f"{suite}.ood_scored.predictions.jsonl"
                    ),
                }
                if record["exists"]:
                    checks, ids = inspect_jsonl(primary)
                    record.update(checks)
                    ids_by_suite_model[(suite, model)] = ids
                records.append(record)

    support: list[dict[str, Any]] = []
    model_order = list(RUN_DIRS)
    for split, suites in (("D", D_SUITES), ("OOD", OOD_SUITES)):
        for suite in suites:
            found = [
                model for model in model_order if (suite, model) in ids_by_suite_model
            ]
            item: dict[str, Any] = {
                "split": split,
                "suite": suite,
                "models_found": found,
                "all_four": len(found) == len(model_order),
            }
            if item["all_four"]:
                sequences = [ids_by_suite_model[(suite, model)] for model in model_order]
                sets = [set(sequence) for sequence in sequences]
                common = set.intersection(*sets)
                union = set.union(*sets)
                ordered_common = [identifier for identifier in sequences[0] if identifier in common]
                item.update(
                    {
                        "rows": {
                            model: len(ids_by_suite_model[(suite, model)])
                            for model in model_order
                        },
                        "set_equal": all(value == sets[0] for value in sets[1:]),
                        "order_equal": all(
                            value == sequences[0] for value in sequences[1:]
                        ),
                        "common_size": len(common),
                        "union_size": len(union),
                        "ordered_common_id_sha256": ordered_id_digest(ordered_common),
                    }
                )
            support.append(item)

    present = [record for record in records if record["exists"]]
    valid_present = all(
        record["bad_json"] == 0
        and record["missing_id"] == 0
        and record["empty_output"] == 0
        and record["duplicate_ids"] == 0
        for record in present
    )
    schema_profiles = sorted(
        {tuple(record["fields"]) for record in present}
    )
    metric_profiles = sorted(
        {tuple(record["metrics_fields"]) for record in present}
    )
    recovery_slots = build_recovery_slots(root, records)
    candidates, hits_by_root = scan_recovery_candidates(
        root, search_roots, recovery_slots
    )
    archive_scan = inspect_archive(archive, recovery_slots)
    eligible_candidates = [
        candidate
        for candidate in candidates
        if candidate["verdict"] == "manual_identity_candidate"
    ]

    return {
        "artifact": "Robot Harness common-support raw prediction bundle manifest",
        "evidence_date": evidence_date,
        "root": str(root.resolve()),
        "path_access": "Windows extended-length path prefix (\\\\?\\)",
        "ordered_id_sha256_contract": (
            "SHA-256 over each UTF-8 ID prefixed by its unsigned 8-byte "
            "big-endian byte length, preserving file order"
        ),
        "run_dirs": RUN_DIRS,
        "summary": {
            "expected_primary_files": len(records),
            "found_primary_files": len(present),
            "missing_primary_files": len(records) - len(present),
            "parsed_rows": sum(record.get("rows", 0) for record in records),
            "total_primary_bytes": sum(record.get("bytes", 0) for record in records),
            "all_present_files_valid": valid_present,
            "schema_aware_files_present": sum(
                bool(record["schema_aware_exists"]) for record in records
            ),
            "ood_scored_files_present": sum(
                bool(record["ood_scored_exists"]) for record in records
            ),
            "four_model_common_support_suites": sum(
                bool(item["all_four"]) for item in support
            ),
            "four_model_exact_set_and_order_suites": sum(
                bool(item.get("set_equal") and item.get("order_equal"))
                for item in support
            ),
            "schema_profile_count": len(schema_profiles),
            "metrics_profile_count": len(metric_profiles),
            "recovery_slots_with_metrics_identity": len(recovery_slots),
            "recovery_candidate_files": len(candidates),
            "eligible_replacement_candidates": len(eligible_candidates),
            "local_source_suite_files_for_missing_slots": sum(
                bool(slot["source_suite_local_exists"]) for slot in recovery_slots
            ),
            "exact_missing_archive_members": (
                archive_scan["exact_missing_target_members"] if archive_scan else None
            ),
        },
        "schema_profiles": [list(profile) for profile in schema_profiles],
        "metrics_profiles": [list(profile) for profile in metric_profiles],
        "common_support": support,
        "records": records,
        "recovery": {
            "search_roots": [str(path.resolve()) for path in search_roots],
            "candidate_hits_by_root": hits_by_root,
            "slots": recovery_slots,
            "candidates": candidates,
            "eligible_candidates": eligible_candidates,
            "archive_scan": archive_scan,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-date", default="2026-07-20")
    parser.add_argument("--search-root", type=Path, action="append", default=[])
    parser.add_argument("--archive", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    search_roots = args.search_root or [args.root]
    manifest = build_manifest(
        args.root, args.evidence_date, search_roots, args.archive
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest["summary"], ensure_ascii=False))
    if not manifest["summary"]["all_present_files_valid"]:
        raise SystemExit("one or more present JSONL files failed validation")


if __name__ == "__main__":
    main()
