#!/usr/bin/env python3
"""Validate the skipping-lectures skill structure, frontmatter, and safety."""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "skipping-lectures"
REFERENCES_DIR = SKILL_DIR / "references"
EXPECTED_PLAYBOOKS = {
    "route-index.md",
    "route-a-transcribe.md",
    "route-b-pan-export.md",
    "cdp-login.md",
    "troubleshooting.md",
}
REQUIRED_SKILL_FIELDS = {"name", "description"}
REQUIRED_PLAYBOOK_FIELDS = {"name", "description"}
MAX_SKILL_DESCRIPTION_CHARS = 600
MAX_SKILL_DESCRIPTION_WORDS = 80
PLACEHOLDER = re.compile(r"\b(?:TODO|FIXME|TBD)\b", re.IGNORECASE)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b"),
    "private key": re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    "Volcengine token": re.compile(r"\b[A-Za-z0-9_-]{32,}="),
}
REMOTE_SHELL_EXECUTION = re.compile(
    r"(?im)^\s*(?:curl|wget|irm|iwr|Invoke-WebRequest)\b[^\r\n]*\|\s*(?:bash|sh|pwsh|powershell|iex)\b"
)
INDEX_ROW = re.compile(r"(?m)^\|\s*`([^`]+)`\s*\|.*?\]\(([^)\s]+)\)\s*\|")


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    fields: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors: list[str] = []

    if not SKILL_DIR.is_dir():
        print(f"FAIL: skill dir missing: {SKILL_DIR}")
        return 1

    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.is_file():
        print(f"FAIL: {skill_md} missing")
        return 1
    skill_text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)
    if fm is None:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        missing = REQUIRED_SKILL_FIELDS - set(fm)
        if missing:
            errors.append(f"SKILL.md: missing frontmatter fields: {sorted(missing)}")
        desc = fm.get("description", "")
        if len(desc) > MAX_SKILL_DESCRIPTION_CHARS:
            errors.append(
                f"SKILL.md: description too long ({len(desc)} chars, max {MAX_SKILL_DESCRIPTION_CHARS})"
            )
        if len(desc.split()) > MAX_SKILL_DESCRIPTION_WORDS:
            errors.append(
                f"SKILL.md: description too long ({len(desc.split())} words, max {MAX_SKILL_DESCRIPTION_WORDS})"
            )

    files = {p.name for p in REFERENCES_DIR.glob("*.md")}
    if files != EXPECTED_PLAYBOOKS:
        errors.append(
            f"references: file set mismatch. missing={sorted(EXPECTED_PLAYBOOKS - files)} extra={sorted(files - EXPECTED_PLAYBOOKS)}"
        )

    index_text = (REFERENCES_DIR / "route-index.md").read_text(encoding="utf-8")
    index_files = {m.group(2).split("/")[-1] for m in INDEX_ROW.finditer(index_text)}
    for f in sorted(index_files - files):
        errors.append(f"route-index.md: links to missing file {f}")

    test_prompts = SKILL_DIR / "test-prompts.json"
    if not test_prompts.is_file():
        errors.append("test-prompts.json: missing")
    else:
        try:
            prompts = json.loads(test_prompts.read_text(encoding="utf-8"))
            if not isinstance(prompts, list) or len(prompts) < 2:
                errors.append("test-prompts.json: must be a list of at least 2 prompts")
            for p in prompts:
                if not {"id", "prompt", "expected"} <= set(p):
                    errors.append("test-prompts.json: every entry needs id/prompt/expected")
        except json.JSONDecodeError as e:
            errors.append(f"test-prompts.json: invalid JSON ({e})")

    for p in sorted(REFERENCES_DIR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        pfm = parse_frontmatter(text)
        if pfm is None:
            errors.append(f"{p.name}: missing YAML frontmatter")
        else:
            missing = REQUIRED_PLAYBOOK_FIELDS - set(pfm)
            if missing:
                errors.append(f"{p.name}: missing frontmatter fields: {sorted(missing)}")

    for p in [skill_md, *REFERENCES_DIR.glob("*.md")]:
        text = p.read_text(encoding="utf-8")
        if PLACEHOLDER.search(text):
            errors.append(f"{p.name}: contains TODO/FIXME/TBD placeholder")
        if REMOTE_SHELL_EXECUTION.search(text):
            errors.append(f"{p.name}: contains remote pipe-to-shell execution")
        for name, pat in SECRET_PATTERNS.items():
            if pat.search(text):
                errors.append(f"{p.name}: possible {name} found")

    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: skipping-lectures skill is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
