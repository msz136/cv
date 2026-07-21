#!/usr/bin/env python3
"""Deterministic static audit for the VLA interview repository.

The validator is intentionally read-only.  It checks the repository contract
described in AGENTS.md: Markdown is canonical, every canonical page has an
HTML/review triplet, the source SHA is synchronized, and rendered pages use
ARIS academic v1 with safe MathJax/heading/link behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


INLINE_OPEN = re.compile(r"\\\(|\\\[|\$\$")
INLINE_CLOSE = re.compile(r"\\\)|\\\]|\$\$")
LOCAL_LINK = re.compile(r'href="(?!https?://|#)([^"]+)"')
H1 = re.compile(r"<h1\b", re.I)
FORMULA = re.compile(r'<div class="formula"[^>]*>([\s\S]*?)</div>', re.I)
FORMULA_EM = re.compile(r"<em\b", re.I)
QA_BLOCK = re.compile(r'<details class="qa">([\s\S]*?)</details>')
QA_ID = re.compile(r"<summary>[\s\S]*?<b>([^<]+)</b>")


def canonical_markdown(root: Path) -> list[Path]:
    excluded = {"README.md", "module_progress.md"}
    return sorted(
        p
        for p in root.rglob("*.md")
        if p.name not in excluded and not p.name.endswith(".question_list.md")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_pages(root: Path, pages: list[Path]) -> dict[str, list[str]]:
    failures: dict[str, list[str]] = {
        "missing_triplets": [],
        "sha_mismatch": [],
        "h1": [],
        "formula_em": [],
        "math_balance": [],
        "local_links": [],
    }
    for md in pages:
        html = md.with_suffix(".html")
        review = md.with_suffix(".review.json")
        rel = md.relative_to(root).as_posix()
        if not html.exists() or not review.exists():
            failures["missing_triplets"].append(rel)
            continue
        try:
            record = json.loads(review.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures["sha_mismatch"].append(f"{rel}: invalid review JSON ({exc})")
            continue
        if record.get("source_sha256", "").lower() != sha256(md):
            failures["sha_mismatch"].append(rel)

        source = md.read_text(encoding="utf-8")
        rendered = html.read_text(encoding="utf-8", errors="replace")
        if len(H1.findall(rendered)) != 1:
            failures["h1"].append(rel)
        if any(FORMULA_EM.search(block) for block in FORMULA.findall(rendered)):
            failures["formula_em"].append(rel)
        if len(INLINE_OPEN.findall(source)) != len(INLINE_CLOSE.findall(source)):
            failures["math_balance"].append(rel)
        for target in LOCAL_LINK.findall(rendered):
            if not (html.parent / target).resolve().exists():
                failures["local_links"].append(f"{rel} -> {target}")
    return failures


def check_academic_html(root: Path) -> dict[str, list[str]]:
    htmls = list(root.rglob("*.html"))
    outer = root.parent / "vla_interview_roadmap.html"
    if outer.exists():
        htmls.append(outer)
    failures: dict[str, list[str]] = {
        "academic_template": [],
        "palette": [],
        "serif": [],
        "sticky_toc": [],
        "responsive": [],
        "mathjax": [],
        "highlight": [],
        "overflow": [],
        "h1": [],
    }
    for html in sorted(set(htmls)):
        rel = str(html)
        text = html.read_text(encoding="utf-8", errors="replace")
        tests = {
            "academic_template": "ARIS render-html (academic, v1)" in text,
            "palette": "#fdfcf7" in text and "#f4f1ea" in text,
            "serif": "Source Serif" in text and "Georgia" in text,
            "sticky_toc": bool(re.search(r"position:\s*sticky", text)) and "260px" in text,
            "responsive": bool(re.search(r"@media\s*\(max-width:\s*900px\)", text)),
            "mathjax": "cdn.jsdelivr.net/npm/mathjax@3" in text,
            "highlight": "highlight.js" in text or "hljs" in text,
            "overflow": "overflow-x:auto" in text or "overflow-x: auto" in text,
            "h1": len(H1.findall(text)) == 1,
        }
        for name, passed in tests.items():
            if not passed:
                failures[name].append(rel)
    return failures


def check_cards(root: Path) -> dict[str, object]:
    ids: list[str] = []
    unseen = 0
    for md in sorted((root / "questions").glob("*.md")):
        if md.name.endswith(".question_list.md"):
            continue
        for block in QA_BLOCK.findall(md.read_text(encoding="utf-8")):
            match = QA_ID.search(block)
            if not match:
                continue
            ids.append(match.group(1).strip())
            if re.search(r"练习状态\*\*[：:]\s*`?unseen`?", block):
                unseen += 1
    return {
        "cards": len(ids),
        "unique_ids": len(set(ids)),
        "duplicate_ids": len(ids) - len(set(ids)),
        "unseen": unseen,
        "coaching_state": (root / "practice" / "coaching_state.md").exists(),
    }


def check_reconciliation(root: Path, pages: list[Path]) -> tuple[list[str], dict[str, object]]:
    """Keep the durable completion ledger aligned with the filesystem.

    The page-level checks above prove that each artifact is internally synced,
    but they cannot catch a stale aggregate count in the Completion Audit or
    the public README/index.  This check is deliberately narrow and read-only:
    it verifies only counts and review verdict distribution, never mastery.
    """
    failures: list[str] = []
    audit_review = root / "sources" / "repository_completion_audit.review.json"
    if not audit_review.exists():
        return ["missing sources/repository_completion_audit.review.json"], {}

    try:
        record = json.loads(audit_review.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        return [f"invalid repository_completion_audit.review.json: {exc}"], {}

    review_files = [p.with_suffix(".review.json") for p in pages]
    verdicts = Counter()
    for review in review_files:
        try:
            verdicts[json.loads(review.read_text(encoding="utf-8")).get("verdict", "")] += 1
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures.append(f"invalid review JSON while reconciling: {review}: {exc}")

    scope = record.get("scope", {})
    observed = len(pages)
    expected_verdicts = {
        "WARN": verdicts.get("WARN", 0),
        "PASS WITH WARNING": verdicts.get("PASS WITH WARNING", 0),
        "PASS": verdicts.get("PASS", 0),
    }
    if scope.get("canonical_markdown") != observed:
        failures.append(
            f"audit scope canonical_markdown={scope.get('canonical_markdown')} != observed {observed}"
        )
    if scope.get("complete_triplets") != observed:
        failures.append(
            f"audit scope complete_triplets={scope.get('complete_triplets')} != observed {observed}"
        )
    recorded_verdicts = record.get("review_distribution_current", {})
    if recorded_verdicts != expected_verdicts:
        failures.append(
            f"audit review distribution={recorded_verdicts} != observed {expected_verdicts}"
        )

    readme = root / "README.md"
    expected_phrase = f"{observed}/{observed} canonical artifacts"
    if readme.exists() and expected_phrase not in readme.read_text(encoding="utf-8"):
        failures.append(f"README.md does not advertise current count phrase: {expected_phrase}")

    expected_p0_audits = {
        "wm019_wam_p0_bundle_audit",
        "openpivla_p0_bundle_audit",
        "robot_harness_p0_bundle_audit",
        "opd_p0_bundle_audit",
        "uwm_libero_p0_bundle_audit",
    }
    audit_dir = root / "evidence" / "projects"
    observed_p0 = {
        p.stem
        for p in audit_dir.glob("*_p0_bundle_audit.md")
    }
    if observed_p0 != expected_p0_audits:
        failures.append(
            f"P0 audit coverage={sorted(observed_p0)} != expected {sorted(expected_p0_audits)}"
        )
    for stem in expected_p0_audits:
        review = audit_dir / f"{stem}.review.json"
        if not review.exists():
            failures.append(f"missing P0 audit review: evidence/projects/{review.name}")

    return failures, {
        "audit_canonical_markdown": scope.get("canonical_markdown"),
        "audit_complete_triplets": scope.get("complete_triplets"),
        "observed_review_distribution": expected_verdicts,
        "p0_audit_coverage": len(observed_p0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    pages = canonical_markdown(root)
    failures = check_pages(root, pages)
    failures.update({f"html_{k}": v for k, v in check_academic_html(root).items()})
    cards = check_cards(root)
    reconciliation_failures, reconciliation = check_reconciliation(root, pages)
    failures["reconciliation"] = reconciliation_failures

    counts = Counter()
    for key, values in failures.items():
        counts[key] = len(values)
    failed = any(values for values in failures.values()) or cards["duplicate_ids"] or cards["coaching_state"]
    result = {
        "root": str(root),
        "canonical_markdown": len(pages),
        "failures": counts,
        "cards": cards,
        "reconciliation": reconciliation,
        "status": "FAIL" if failed else "PASS",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failed:
        for key, values in failures.items():
            if values:
                print(f"\n[{key}]", file=sys.stderr)
                print("\n".join(values[:20]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
