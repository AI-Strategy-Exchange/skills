#!/usr/bin/env python3
"""
Validate a skill directory against the Agent Skills spec plus the
frontmatter fields Claude Code documents at
https://code.claude.com/docs/en/skills#frontmatter-reference.

For the authoritative parse that Claude Code itself runs, also use
`claude plugin validate <dir>` (Claude Code v2.1.233+).

Usage:
    python3 scripts/validate_skill.py <skill_directory>

Exit codes: 0 = valid, 1 = invalid

Requires PyYAML (see scripts/requirements.txt).
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is not installed.\n"
        "  pip install -r scripts/requirements.txt\n"
        "or: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

# Common Claude Code built-in tools. The tool roster changes between
# releases, so a name outside this set is a warning, not an error.
# MCP tools follow mcp__<server>__<tool>.
KNOWN_TOOLS = {
    "Agent", "Bash", "Edit", "Glob", "Grep", "NotebookEdit", "Read",
    "Skill", "TodoWrite", "WebFetch", "WebSearch", "Write",
}

PORTABLE_KEYS = {
    "name", "description", "license", "allowed-tools",
    "metadata", "compatibility",
}

# Fields Claude Code adds. claude.ai and the Skills API may reject them on upload.
CLAUDE_CODE_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context",
    "agent", "background", "hooks", "paths", "shell",
}

ALLOWED_FRONTMATTER_KEYS = PORTABLE_KEYS | CLAUDE_CODE_KEYS

BOOLEAN_KEYS = {"disable-model-invocation", "user-invocable"}

# Claude Code truncates description + when_to_use to this many characters
# in the skill listing it puts in context.
LISTING_CHAR_CAP = 1536

OPTIONAL_STRING_KEYS = {"when_to_use", "compatibility", "license"}


def parse_tool_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    # Separators inside a permission pattern belong to it: "Bash(git add *)" is one entry.
    entries, current, depth = [], "", 0
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        if depth == 0 and (ch.isspace() or ch == ","):
            if current:
                entries.append(current)
            current = ""
        else:
            current += ch
    if current:
        entries.append(current)
    return entries


def validate_skill(skill_path):
    """
    Validate a skill directory.

    Returns (valid: bool, message: str).
    Collects all issues instead of stopping at the first one.
    """
    skill_path = Path(skill_path)
    issues = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return False, "No YAML frontmatter found (file must start with ---)"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter: missing closing ---"

    try:
        fm = yaml.safe_load(match.group(1))
        if not isinstance(fm, dict):
            return False, "Frontmatter must be a YAML mapping"
    except yaml.YAMLError as e:
        return False, f"YAML parse error in frontmatter: {e}"

    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        issues.append(
            f"Unknown frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    if "name" not in fm:
        issues.append("Missing required field: 'name'")
    if "description" not in fm:
        issues.append("Missing required field: 'description'")

    name = fm.get("name", "")
    if not isinstance(name, str):
        issues.append(f"'name' must be a string, got {type(name).__name__}")
    else:
        name = name.strip()
        if name:
            if not re.match(r"^[a-z0-9-]+$", name):
                issues.append(
                    f"Name '{name}' must be kebab-case (lowercase letters, digits, hyphens only)"
                )
            elif name.startswith("-") or name.endswith("-") or "--" in name:
                issues.append(
                    f"Name '{name}' cannot start/end with a hyphen or contain consecutive hyphens"
                )
            if len(name) > 64:
                issues.append(f"Name too long ({len(name)} chars, max 64)")

            if skill_path.name != name:
                issues.append(
                    f"Directory name '{skill_path.name}' does not match frontmatter name '{name}'"
                )

    desc = fm.get("description", "")
    if not isinstance(desc, str):
        issues.append(f"'description' must be a string, got {type(desc).__name__}")
    else:
        desc = desc.strip()
        if desc:
            if "<" in desc or ">" in desc:
                issues.append("Description cannot contain angle brackets (< or >)")
            if len(desc) > 1024:
                issues.append(f"Description too long ({len(desc)} chars, max 1024)")
            if len(desc) < 40:
                warnings.append(
                    f"Description is short ({len(desc)} chars) — "
                    "trigger reliability improves with concrete when-to-use phrasing"
                )

    for key in sorted(OPTIONAL_STRING_KEYS & fm.keys()):
        if not isinstance(fm[key], str):
            issues.append(f"'{key}' must be a string, got {fm[key]!r}")

    when_to_use = fm.get("when_to_use")
    if not isinstance(when_to_use, str):
        when_to_use = ""
    if isinstance(desc, str):
        listed = len(desc.strip()) + len(when_to_use.strip())
        if listed > LISTING_CHAR_CAP:
            warnings.append(
                f"description + when_to_use is {listed} chars; Claude Code truncates "
                f"it to {LISTING_CHAR_CAP} in the skill listing, so put the key use case first"
            )

    for key in sorted(BOOLEAN_KEYS & fm.keys()):
        if not isinstance(fm[key], bool):
            issues.append(f"'{key}' must be true or false, got {fm[key]!r}")

    if fm.get("disable-model-invocation") is True and fm.get("user-invocable") is False:
        warnings.append(
            "disable-model-invocation: true with user-invocable: false hides the skill "
            "from both Claude and the / menu"
        )

    claude_code_only = sorted(CLAUDE_CODE_KEYS & fm.keys())
    if claude_code_only:
        warnings.append(
            f"Claude Code-only field(s): {', '.join(claude_code_only)}. "
            "Check they are accepted before uploading to claude.ai or the Skills API"
        )

    compat = fm.get("compatibility")
    if isinstance(compat, str) and len(compat) > 500:
        issues.append(f"Compatibility too long ({len(compat)} chars, max 500)")

    allowed_tools = fm.get("allowed-tools")
    if allowed_tools is not None:
        if not isinstance(allowed_tools, (str, list)):
            issues.append("'allowed-tools' must be a string or a YAML list")
        else:
            tools = parse_tool_list(allowed_tools)
            unknown_tools = []
            mcp_tools = []
            for entry in tools:
                tool = entry.split("(", 1)[0]
                if tool.startswith("mcp__"):
                    parts = tool.split("__")
                    if len(parts) != 3 or not all(parts):
                        issues.append(
                            f"MCP tool '{tool}' must follow mcp__<server>__<tool> format"
                        )
                    else:
                        mcp_tools.append(tool)
                elif tool not in KNOWN_TOOLS:
                    unknown_tools.append(tool)
            if unknown_tools:
                warnings.append(
                    f"Unrecognized tool(s) in allowed-tools: {', '.join(unknown_tools)}. "
                    "Check the spelling against Claude Code's current tool list"
                )
            if "Bash" in tools:
                warnings.append(
                    "Unscoped Bash in allowed-tools grants all shell commands; "
                    "prefer a pattern such as Bash(git status *)"
                )
            for mcp_tool in mcp_tools:
                server = mcp_tool.split("__")[1]
                if server not in content:
                    warnings.append(
                        f"MCP server '{server}' declared in allowed-tools but not referenced in SKILL.md body"
                    )

    agents_dir = skill_path / "agents"
    if agents_dir.exists():
        for agent_file in agents_dir.iterdir():
            if agent_file.is_file() and agent_file.suffix != ".md":
                issues.append(
                    f"Agent file '{agent_file.name}' should be a .md file"
                )

    # Only check links that explicitly point into agents/
    agent_link_re = re.compile(r"\]\(agents/([^)\s]+\.md)\)")
    for ref in agent_link_re.findall(content):
        if not (skill_path / "agents" / ref).exists():
            warnings.append(f"Referenced agent file not found: agents/{ref}")

    if issues:
        lines = ["Validation failed:"] + [f"  - {i}" for i in issues]
        if warnings:
            lines += ["Warnings:"] + [f"  - {w}" for w in warnings]
        return False, "\n".join(lines)

    if warnings:
        lines = ["Skill is valid (with warnings):"] + [f"  - {w}" for w in warnings]
        return True, "\n".join(lines)

    return True, "Skill is valid"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_skill.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
