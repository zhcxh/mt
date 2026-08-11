"""
tests/test_examples_syntax.py
------------------------------
Validates that every example file is syntactically correct Python and
that the SKILL.md is well-formed YAML frontmatter + Markdown.

These tests run in CI without needing Scrapling installed.
"""

import ast
import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SKILL_MD = REPO_ROOT / "SKILL.md"


# ---------------------------------------------------------------------------
# Example files: syntax
# ---------------------------------------------------------------------------

def _example_files():
    return sorted(EXAMPLES_DIR.glob("*.py"))


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_syntax(path: pathlib.Path):
    """Every .py file in examples/ must parse as valid Python."""
    source = path.read_text(encoding="utf-8")
    try:
        ast.parse(source)
    except SyntaxError as exc:
        pytest.fail(f"{path.name}: SyntaxError at line {exc.lineno}: {exc.msg}")


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_has_docstring(path: pathlib.Path):
    """Every example should have a module-level docstring."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree)
    assert docstring, f"{path.name} is missing a module-level docstring"


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_has_main_guard(path: pathlib.Path):
    """Every example should have an `if __name__ == '__main__':` guard."""
    source = path.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source, (
        f"{path.name} is missing an `if __name__ == '__main__':` guard"
    )


def test_all_six_examples_exist():
    """Ensure all six documented examples are present."""
    expected = {
        "01_simple_fetch.py",
        "02_session.py",
        "03_stealth.py",
        "04_spider.py",
        "05_adaptive.py",
        "06_hybrid_spider.py",
    }
    found = {p.name for p in _example_files()}
    missing = expected - found
    assert not missing, f"Missing example files: {missing}"


# ---------------------------------------------------------------------------
# SKILL.md: structure
# ---------------------------------------------------------------------------

def test_skill_md_exists():
    assert SKILL_MD.exists(), "SKILL.md not found in repo root"


def test_skill_md_has_frontmatter():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter (---)"
    end = content.index("---", 3)
    frontmatter = content[3:end]
    assert "name:" in frontmatter, "SKILL.md frontmatter must contain 'name:'"
    assert "description:" in frontmatter, "SKILL.md frontmatter must contain 'description:'"


def test_skill_md_line_count():
    lines = SKILL_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 500, (
        f"SKILL.md is {len(lines)} lines — keep it under 500 for fast context loading"
    )


def test_skill_md_has_required_sections():
    content = SKILL_MD.read_text(encoding="utf-8")
    required = [
        "## Step 0",       # fetcher selection
        "## Step 1",       # install
        "## Step 2",       # patterns
        "Selector Reference",
        "Decision Tree",
    ]
    for section in required:
        assert section in content, f"SKILL.md is missing section: {section!r}"


def test_skill_md_no_em_dashes():
    """Enforce house style: no en/em dashes."""
    content = SKILL_MD.read_text(encoding="utf-8")
    # Allow — only in URLs or code blocks; simple heuristic: flag bare ones
    bare_em_dash = re.search(r"(?<![`\[/])\u2014(?![`\]/])", content)
    bare_en_dash = re.search(r"(?<![`\[/])\u2013(?![`\]/])", content)
    assert not bare_em_dash, "SKILL.md contains an em dash (—) — use plain text instead"
    assert not bare_en_dash, "SKILL.md contains an en dash (-) — use a hyphen instead"


# ---------------------------------------------------------------------------
# README: completeness
# ---------------------------------------------------------------------------

README = REPO_ROOT / "README.md"

def test_readme_exists():
    assert README.exists(), "README.md not found"


def test_readme_has_install_section():
    content = README.read_text(encoding="utf-8")
    assert "git clone" in content, "README.md should include a git clone install command"


def test_readme_links_all_examples():
    content = README.read_text(encoding="utf-8")
    for i in range(1, 7):
        assert f"0{i}_" in content, f"README.md does not link example 0{i}"
