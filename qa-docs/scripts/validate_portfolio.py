from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CASE_FIELDS = [
    "ID",
    "Title",
    "Requirement",
    "Preconditions",
    "Test data",
    "Steps",
    "Expected result",
    "Priority",
    "Type",
    "Platform",
    "Automation candidate",
]
REQUIRED_BUG_FIELDS = [
    "ID",
    "Title",
    "Environment",
    "Preconditions",
    "Steps to reproduce",
    "Actual result",
    "Expected result",
    "Reproducibility",
    "Severity",
    "Priority",
    "Affected requirement",
    "Attachments/evidence",
    "Business impact",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf8")


def requirements() -> set[str]:
    text = read(ROOT / "requirements" / "product-requirements.md")
    return set(re.findall(r"REQ-\d{3}", text))


def field_value(text: str, field: str) -> str | None:
    match = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def validate_cases(reqs: set[str]) -> dict[str, int]:
    seen: set[str] = set()
    counts = {"WEB": 0, "MOB": 0, "API": 0, "E2E": 0}
    for path in sorted((ROOT / "test-cases").glob("*/*.md")):
        text = read(path)
        for field in REQUIRED_CASE_FIELDS:
            if field_value(text, field) is None:
                raise SystemExit(f"Missing field {field} in {path}")
        case_id = field_value(text, "ID")
        if case_id in seen:
            raise SystemExit(f"Duplicate test case id: {case_id}")
        seen.add(case_id)
        req = field_value(text, "Requirement")
        if req not in reqs:
            raise SystemExit(f"Unknown requirement {req} in {path}")
        prefix = case_id.split("-")[0]
        if prefix not in counts:
            raise SystemExit(f"Unexpected test case prefix: {case_id}")
        counts[prefix] += 1
    if sum(counts.values()) < 90:
        raise SystemExit("Expected at least 90 test cases")
    minimums = {"WEB": 35, "MOB": 20, "API": 25, "E2E": 10}
    for prefix, minimum in minimums.items():
        if counts[prefix] < minimum:
            raise SystemExit(f"Expected at least {minimum} {prefix} test cases")
    return counts


def validate_bugs(reqs: set[str]) -> int:
    bug_files = sorted((ROOT / "bug-reports").glob("BUG-*.md"))
    if len(bug_files) != 15:
        raise SystemExit(f"Expected exactly 15 bug reports, got {len(bug_files)}")
    seen: set[str] = set()
    expected = {f"BUG-{i:03d}" for i in range(1, 16)}
    for path in bug_files:
        text = read(path)
        for field in REQUIRED_BUG_FIELDS:
            if field_value(text, field) is None:
                raise SystemExit(f"Missing bug field {field} in {path}")
        bug_id = field_value(text, "ID")
        if bug_id in seen:
            raise SystemExit(f"Duplicate bug id: {bug_id}")
        seen.add(bug_id)
        req = field_value(text, "Affected requirement")
        if req not in reqs:
            raise SystemExit(f"Unknown affected requirement {req} in {path}")
        evidence_match = re.search(r"\((?:\.\./)?(evidence/[^)]+)\)", text)
        if not evidence_match:
            raise SystemExit(f"Missing evidence link in {path}")
        if not (ROOT / evidence_match.group(1)).exists():
            raise SystemExit(f"Missing evidence file {evidence_match.group(1)}")
    if seen != expected:
        raise SystemExit("Bug IDs must be BUG-001...BUG-015")
    return len(bug_files)


def validate_links() -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        text = read(path)
        for raw_target in link_pattern.findall(text):
            if raw_target.startswith(("http://", "https://", "mailto:")):
                continue
            target = raw_target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                raise SystemExit(f"Broken relative link in {path}: {raw_target}")


def validate_stats(counts: dict[str, int], bug_count: int) -> None:
    readme = read(ROOT / "README.md")
    expected_lines = [
        f"- Web test cases: {counts['WEB']}",
        f"- Mobile test cases: {counts['MOB']}",
        f"- API test cases: {counts['API']}",
        f"- E2E test cases: {counts['E2E']}",
        f"- Total test cases: {sum(counts.values())}",
        f"- Bug reports: {bug_count}",
    ]
    for line in expected_lines:
        if line not in readme:
            raise SystemExit(f"README stats are stale: {line}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    reqs = requirements()
    counts = validate_cases(reqs)
    bug_count = validate_bugs(reqs)
    validate_links()
    validate_stats(counts, bug_count)
    print(
        "OK: "
        f"Web={counts['WEB']}, Mobile={counts['MOB']}, "
        f"API={counts['API']}, E2E={counts['E2E']}, "
        f"Total={sum(counts.values())}, Bugs={bug_count}"
    )


if __name__ == "__main__":
    main()
