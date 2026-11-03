import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/advanced-skill-creator/scripts"))

from validate_skill import parse_tool_list, validate_skill

DESC = "description: Deploy the app to production when the user asks for a release."


def make_skill(tmp_path, *lines):
    skill = tmp_path / "demo"
    skill.mkdir()
    frontmatter = "\n".join(["name: demo", *lines])
    (skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\nbody\n")
    return skill


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Bash(git add *) Bash(git commit *)", ["Bash(git add *)", "Bash(git commit *)"]),
        ("Read, Write mcp__gh__pr", ["Read", "Write", "mcp__gh__pr"]),
        ("Bash(foo(bar) *) Read", ["Bash(foo(bar) *)", "Read"]),
        ("Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)", ["Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)"]),
        (["Bash(git add *)", "Read"], ["Bash(git add *)", "Read"]),
    ],
)
def test_parse_tool_list(value, expected):
    assert parse_tool_list(value) == expected


def test_claude_code_fields_accepted(tmp_path):
    skill = make_skill(
        tmp_path,
        DESC,
        "when_to_use: Say ship it or cut a release.",
        "disable-model-invocation: true",
        "allowed-tools:",
        "  - Bash(git tag *)",
        "  - Read",
    )
    valid, message = validate_skill(skill)
    assert valid, message
    assert "Unrecognized tool" not in message


def test_unknown_key_rejected(tmp_path):
    valid, message = validate_skill(make_skill(tmp_path, DESC, "foo: bar"))
    assert not valid
    assert "Unknown frontmatter key(s): foo" in message


@pytest.mark.parametrize("value", ["null", "false", "[]", "3"])
@pytest.mark.parametrize("key", ["when_to_use", "compatibility", "license"])
def test_optional_string_fields_reject_non_strings(tmp_path, key, value):
    valid, message = validate_skill(make_skill(tmp_path, DESC, f"{key}: {value}"))
    assert not valid
    assert f"'{key}' must be a string" in message


def test_boolean_fields_reject_strings(tmp_path):
    valid, message = validate_skill(make_skill(tmp_path, DESC, 'disable-model-invocation: "yes"'))
    assert not valid
    assert "'disable-model-invocation' must be true or false" in message


def test_listing_cap_warning(tmp_path):
    skill = make_skill(tmp_path, f"description: {'x' * 1000}", f"when_to_use: {'y' * 600}")
    valid, message = validate_skill(skill)
    assert valid, message
    assert "1600 chars" in message


def test_unscoped_bash_warns_but_pattern_does_not(tmp_path):
    _, unscoped = validate_skill(make_skill(tmp_path, DESC, "allowed-tools: Bash Read"))
    assert "Unscoped Bash" in unscoped
    (tmp_path / "demo" / "SKILL.md").unlink()
    (tmp_path / "demo").rmdir()
    _, scoped = validate_skill(make_skill(tmp_path, DESC, "allowed-tools: Bash(git status *)"))
    assert "Unscoped Bash" not in scoped
