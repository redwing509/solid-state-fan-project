"""Offline checks for the thermal1d dependency floors.

The manifest is read with a small TOML reader so the same tests run on
Python 3.9, 3.10, and 3.12. On 3.11 and newer the reader is compared with
the standard-library parser. Nothing in this module contacts the network.

pytest stays a test extra below 9.0.3 because that fix requires Python
>=3.10. setuptools stays a build requirement at 78.1.1 or newer, which
still supports Python >=3.9.
"""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "engines" / "thermal1d" / "pyproject.toml"
REQUIREMENTS = ROOT / "engines" / "thermal1d" / "requirements.txt"


def version_key(value):
    parts = []
    for piece in str(value).split("."):
        number = ""
        for character in piece:
            if character.isdigit():
                number += character
            else:
                break
        parts.append(int(number) if number else 0)
    return tuple(parts)


def version_ge(left, right):
    left_key, right_key = version_key(left), version_key(right)
    width = max(len(left_key), len(right_key))
    left_key += (0,) * (width - len(left_key))
    right_key += (0,) * (width - len(right_key))
    return left_key >= right_key


def python_allows(specifier, version):
    if not specifier:
        return True
    for part in (item.strip() for item in specifier.split(",")):
        if not part:
            continue
        if part.startswith(">="):
            if not version_ge(version, part[2:]):
                return False
        elif part.startswith("<="):
            if not version_ge(part[2:], version):
                return False
        elif part.startswith(">"):
            if not version_ge(version, part[1:]) or version_key(version) == version_key(part[1:]):
                return False
        elif part.startswith("<"):
            if version_ge(version, part[1:]):
                return False
        elif part.startswith("=="):
            if version_key(version) != version_key(part[2:]):
                return False
        elif part.startswith("!="):
            if version_key(version) == version_key(part[2:]):
                return False
        else:
            raise AssertionError("unsupported requires-python term: " + part)
    return True


def lower_bound(requirement):
    requirement = requirement.split(";", 1)[0].split("#", 1)[0].strip()
    name, separator, version = requirement.partition(">=")
    if separator != ">=" or not version or any(token in version for token in ",<>!"):
        raise AssertionError("expected a minimum floor, got " + requirement)
    return name.strip().lower(), version.strip()


def requirement_names(values):
    names = []
    for value in values:
        body = value.split(";", 1)[0].split("#", 1)[0]
        if ">=" in body:
            names.append(lower_bound(value)[0])
        else:
            names.append(body.strip().lower())
    return names


def _strip_comment(line):
    in_basic = False
    in_literal = False
    escaped = False
    kept = []
    for character in line:
        if in_basic:
            kept.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_basic = False
            continue
        if in_literal:
            kept.append(character)
            if character == "'":
                in_literal = False
            continue
        if character == "#":
            break
        kept.append(character)
        if character == '"':
            in_basic = True
        elif character == "'":
            in_literal = True
    return "".join(kept)


def _parse_basic_string(text, start):
    if text[start] != '"':
        raise ValueError("expected a quoted string")
    characters = []
    index = start + 1
    escapes = {"\\": "\\", '"': '"', "n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}
    while index < len(text):
        character = text[index]
        if character == '"':
            return "".join(characters), index + 1
        if character == "\\":
            index += 1
            if index >= len(text) or text[index] not in escapes:
                raise ValueError("unsupported string escape")
            characters.append(escapes[text[index]])
        else:
            characters.append(character)
        index += 1
    raise ValueError("unterminated string")


def _parse_literal_string(text, start):
    if text[start] != "'":
        raise ValueError("expected a literal string")
    end = text.find("'", start + 1)
    if end < 0:
        raise ValueError("unterminated literal string")
    return text[start + 1:end], end + 1


def _parse_array(text, start):
    if text[start] != "[":
        raise ValueError("expected an array")
    index = start + 1
    values = []
    while index < len(text):
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
        if index < len(text) and text[index] == "]":
            return values, index + 1
        value, index = _parse_value_at(text, index)
        values.append(value)
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
        if index < len(text) and text[index] == ",":
            index += 1
            continue
        if index < len(text) and text[index] == "]":
            continue
        raise ValueError("malformed array")
    raise ValueError("unterminated array")


def _parse_value_at(text, start):
    while start < len(text) and text[start] in " \t\r\n":
        start += 1
    if start >= len(text):
        raise ValueError("missing value")
    if text[start] == '"':
        return _parse_basic_string(text, start)
    if text[start] == "'":
        return _parse_literal_string(text, start)
    if text[start] == "[":
        return _parse_array(text, start)
    raise ValueError("unsupported TOML value")


def _parse_value(text):
    value, index = _parse_value_at(text, 0)
    if text[index:].strip():
        raise ValueError("trailing TOML value: " + text[index:])
    return value


def parse_toml(text):
    """Read the subset of TOML used by engines/thermal1d/pyproject.toml."""
    root = {}
    current = root
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if line.startswith("["):
            if not line.endswith("]") or line.startswith("[["):
                raise ValueError("unsupported table on line %s" % line_number)
            parts = [part.strip() for part in line[1:-1].split(".")]
            if not parts or any(not part or any(ch in part for ch in "[]=#'\"") for part in parts):
                raise ValueError("invalid table on line %s" % line_number)
            current = root
            for part in parts:
                node = current.get(part)
                if node is None:
                    node = {}
                    current[part] = node
                elif not isinstance(node, dict):
                    raise ValueError("table collides with a value on line %s" % line_number)
                current = node
            continue
        key, separator, raw_value = line.partition("=")
        key = key.strip()
        if not separator or not key or any(ch in key for ch in ".[]#'\""):
            raise ValueError("unsupported assignment on line %s" % line_number)
        try:
            current[key] = _parse_value(raw_value.strip())
        except ValueError as error:
            raise ValueError("line %s: %s" % (line_number, error))
    return root


def load_manifest():
    text = PYPROJECT.read_text(encoding="utf-8")
    parsed = parse_toml(text)
    if sys.version_info >= (3, 11):
        import tomllib
        if parsed != tomllib.loads(text):
            raise AssertionError("TOML reader does not match tomllib")
    return parsed


class DependencyFloorTests(unittest.TestCase):
    def setUp(self):
        self.project = load_manifest()

    def test_python_3_9_support_is_unchanged(self):
        requires_python = self.project["project"]["requires-python"]
        self.assertEqual(requires_python, ">=3.9")
        self.assertTrue(python_allows(requires_python, "3.9"))
        self.assertTrue(python_allows(requires_python, "3.10"))
        self.assertTrue(python_allows(requires_python, "3.12"))
        self.assertFalse(python_allows(">=3.10", "3.9"))

    def test_setuptools_floor_is_build_only_and_excludes_package_index_range(self):
        build = [lower_bound(item) for item in self.project["build-system"]["requires"]]
        self.assertEqual([name for name, _version in build], ["setuptools"])
        _name, floor = build[0]
        self.assertTrue(version_ge(floor, "78.1.1"))
        for vulnerable in ("61", "65.5.0", "69.1.1", "70.0.0", "78.1.0"):
            self.assertFalse(version_ge(vulnerable, floor), vulnerable)
        self.assertTrue(version_ge("78.1.1", floor))
        runtime = requirement_names(self.project["project"]["dependencies"])
        self.assertEqual(runtime, ["numpy"])
        self.assertNotIn("setuptools", runtime)
        self.assertNotIn("pytest", runtime)

    def test_pytest_remains_a_test_extra_below_the_py310_only_fix(self):
        test_extra = [lower_bound(item) for item in self.project["project"]["optional-dependencies"]["test"]]
        floors = dict(test_extra)
        self.assertIn("pytest", floors)
        self.assertFalse(version_ge(floors["pytest"], "9.0.3"))
        self.assertNotIn("pytest", requirement_names(self.project["project"]["dependencies"]))
        requirement_floors = dict(
            lower_bound(line)
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.split("#", 1)[0].strip()
        )
        self.assertEqual(requirement_floors["pytest"], floors["pytest"])
        self.assertNotIn("setuptools", requirement_floors)


if __name__ == "__main__":
    unittest.main()
