#!/usr/bin/env python3
"""Lint the repo's MiMo Code command, agent, config, and skill files.

Run from anywhere: python tools/lint_mimocode_skills.py

Checks:
- Every .mimocode/commands/*.md file has YAML frontmatter that parses, with a
  non-empty `description` key
- Every .mimocode/agents/*.md file has YAML frontmatter that parses, with
  non-empty `description` and `mode` keys, and `mode` is exactly "subagent"
  or "primary"
- .mimocode/mimocode.json is valid JSON, is a top-level object, and has a
  `permission` key that is an object
- Every SKILL.md (.claude/skills/*, .agents/skills/*) has YAML frontmatter
  that parses, with non-empty `name` and `description` keys (unchanged by
  the MiMo migration - reuses the same check as tools/lint_skills.py)
- Cross-reference: for each .mimocode/commands/*.md file whose body mentions
  a `.mimocode/agents/<x>.md` path, that file actually exists

Exit code 0 on success, 1 with a failure list otherwise.
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("lint_mimocode_skills.py requires PyYAML: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

AGENT_REF_RE = re.compile(r"\.mimocode/agents/[\w\-]+\.md")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_frontmatter(path: Path) -> dict | None:
    """Return the parsed frontmatter mapping, or None (after recording an error)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{rel(path)}: missing YAML frontmatter (file must start with ---)")
        return None
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{rel(path)}: unterminated YAML frontmatter")
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: frontmatter did not parse to a mapping")
        return None
    return data


def check_command(path: Path) -> None:
    data = parse_frontmatter(path)
    if data is None:
        return
    if not data.get("description"):
        errors.append(f"{rel(path)}: frontmatter missing required key 'description'")

    # Cross-reference check: any .mimocode/agents/<x>.md path mentioned in the
    # body must actually exist, so a renamed/deleted subagent file is caught.
    text = path.read_text(encoding="utf-8")
    for match in sorted(set(AGENT_REF_RE.findall(text))):
        target = ROOT / match
        if not target.is_file():
            errors.append(f"{rel(path)}: references missing subagent file '{match}'")


def check_agent(path: Path) -> None:
    data = parse_frontmatter(path)
    if data is None:
        return
    if not data.get("description"):
        errors.append(f"{rel(path)}: frontmatter missing required key 'description'")
    mode = data.get("mode")
    if not mode:
        errors.append(f"{rel(path)}: frontmatter missing required key 'mode'")
    elif mode not in ("subagent", "primary"):
        errors.append(f"{rel(path)}: frontmatter 'mode' must be 'subagent' or 'primary', got {mode!r}")


def check_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{rel(path)}: missing YAML frontmatter (file must start with ---)")
        return
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{rel(path)}: unterminated YAML frontmatter")
        return
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: frontmatter is not valid YAML: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: frontmatter did not parse to a mapping")
        return
    for key in ("name", "description"):
        if not data.get(key):
            errors.append(f"{rel(path)}: frontmatter missing required key '{key}'")

    allowed = data.get("allowed-tools", "")
    if isinstance(allowed, str):
        for match in re.finditer(r"bun run ([^\s)]+)", allowed):
            target = match.group(1).rstrip("*")
            if not target or target.endswith("/"):
                continue
            # Targets may contain globs (e.g. .agents/skills/*/cli/src/cli.ts);
            # require at least one existing file to match.
            if "*" in target:
                if not list(ROOT.glob(target)) and not list((ROOT / ".agents").glob(target)):
                    errors.append(f"{rel(path)}: allowed-tools glob matches no files: {target}")
            else:
                candidates = [ROOT / target, ROOT / ".agents" / target]
                if not any(c.is_file() for c in candidates):
                    errors.append(f"{rel(path)}: allowed-tools references a missing file: {target}")


def check_mimocode_json() -> None:
    path = ROOT / ".mimocode" / "mimocode.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".mimocode/mimocode.json: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(".mimocode/mimocode.json: expected top-level JSON value to be an object")
        return
    permission = data.get("permission")
    if not isinstance(permission, dict):
        errors.append(".mimocode/mimocode.json: expected 'permission' to be an object")


def main() -> int:
    commands = sorted((ROOT / ".mimocode" / "commands").glob("*.md"))
    agents = sorted((ROOT / ".mimocode" / "agents").glob("*.md"))
    skills = sorted(ROOT.glob(".claude/skills/*/SKILL.md")) + sorted(ROOT.glob(".agents/skills/*/SKILL.md"))

    if not commands:
        errors.append("no command files found under .mimocode/commands/")
    if not agents:
        errors.append("no agent files found under .mimocode/agents/")
    if not skills:
        errors.append("no SKILL.md files found - glob roots are wrong or the tree moved")

    for command in commands:
        check_command(command)
    for agent in agents:
        check_agent(agent)
    for skill in skills:
        check_skill(skill)
    check_mimocode_json()

    if errors:
        print(f"lint_mimocode_skills: {len(errors)} failure(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(
        f"lint_mimocode_skills: OK "
        f"({len(commands)} commands, {len(agents)} agents, {len(skills)} skills, mimocode.json)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
