import os

BUG_IDS = tuple(f"BUG-{number:03d}" for number in range(1, 16))


def bug_mode_enabled() -> bool:
    return os.getenv("QA_BUG_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}


def bug_enabled(bug_id: str) -> bool:
    return bug_mode_enabled() and bug_id in BUG_IDS
