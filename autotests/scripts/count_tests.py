from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_api() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "api-tests", "--collect-only", "-q"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return sum(1 for line in result.stdout.splitlines() if "::test_" in line)


def count_web() -> int:
    total = 0
    for path in (ROOT / "web-tests" / "tests").glob("*.spec.ts"):
        text = path.read_text(encoding="utf8")
        total += len(re.findall(r"^test\(", text, flags=re.MULTILINE))
    return total


def count_mobile() -> int:
    return len(list((ROOT / "mobile-tests" / "maestro").glob("*.yaml")))


def main() -> None:
    api = count_api()
    web = count_web()
    mobile = count_mobile()
    if api < 60:
        raise SystemExit(f"Expected API >= 60, got {api}")
    if web < 36:
        raise SystemExit(f"Expected Web >= 36, got {web}")
    if mobile < 10:
        raise SystemExit(f"Expected Mobile >= 10, got {mobile}")
    print(f"API={api}, Web={web}, Mobile={mobile}")


if __name__ == "__main__":
    main()
