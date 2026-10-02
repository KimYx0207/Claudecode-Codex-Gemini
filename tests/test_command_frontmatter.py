"""Validate command metadata without importing the example application."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, ScalarNode

ROOT = Path(__file__).resolve().parents[1]


class TestCommandFrontmatter(unittest.TestCase):
    def assert_quoted_argument_hint(self, text: str) -> str:
        """Require a string scalar with explicit YAML quotes in frontmatter."""
        match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.S)
        self.assertIsNotNone(match, "missing opening or closing frontmatter delimiter")
        assert match is not None
        frontmatter = match.group(1)
        parsed = yaml.safe_load(frontmatter)
        self.assertIsInstance(parsed, dict, "frontmatter must be a mapping")
        self.assertIn("argument-hint", parsed)
        self.assertIsInstance(parsed["argument-hint"], str, "argument-hint must be a string")
        self.assertTrue(parsed["argument-hint"].strip(), "argument-hint must not be empty")

        node = yaml.compose(frontmatter, Loader=yaml.SafeLoader)
        self.assertIsInstance(node, MappingNode)
        assert isinstance(node, MappingNode)
        hints = [value for key, value in node.value if key.value == "argument-hint"]
        self.assertEqual(len(hints), 1, "argument-hint must occur exactly once")
        self.assertIsInstance(hints[0], ScalarNode)
        self.assertIn(hints[0].style, ('"', "'"), "argument-hint must be explicitly quoted")
        return parsed["argument-hint"]

    def test_all_command_frontmatter(self) -> None:
        commands = sorted((ROOT / ".claude" / "commands").rglob("*.md"))
        self.assertTrue(commands, "no commands found; do not silently skip the regression")
        for command in commands:
            with self.subTest(command=command.relative_to(ROOT)):
                self.assert_quoted_argument_hint(command.read_text(encoding="utf-8"))

    def test_documented_command_frontmatter(self) -> None:
        documentation = (ROOT / "docs" / "claude-code-specs.md").read_text(encoding="utf-8")
        examples = [
            block
            for block in re.findall(r"```(?:markdown|yaml)\r?\n(.*?)```", documentation, re.S)
            if "argument-hint:" in block
        ]
        self.assertTrue(examples, "no documented command example found")
        for example in examples:
            with self.subTest(example=example):
                # An inline YAML comment belongs outside the quoted value (PR #2 review).
                self.assertEqual(self.assert_quoted_argument_hint(example), "[参数描述]")

    def test_regression_rejects_bare_array(self) -> None:
        with self.assertRaises(AssertionError):
            self.assert_quoted_argument_hint("---\nargument-hint: [task]\n---\n")

    def test_regression_rejects_unquoted_string(self) -> None:
        with self.assertRaises(AssertionError):
            self.assert_quoted_argument_hint("---\nargument-hint: task\n---\n")

    def test_quoted_hint_excludes_inline_comment(self) -> None:
        for quote in ('"', "'"):
            with self.subTest(quote=quote):
                self.assertEqual(
                    self.assert_quoted_argument_hint(
                        f"---\nargument-hint: {quote}[task]{quote} # optional hint\n---\n"
                    ),
                    "[task]",
                )


if __name__ == "__main__":
    unittest.main()
