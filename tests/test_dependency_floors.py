"""Build-floor and dependency-resolution checks for thermal1d.

pytest is a test extra. Its reviewed fix, pytest 9.0.3, requires Python >=3.10.
The newest pytest release that still declares Python >=3.9 support is 8.4.2,
which is inside the vulnerable range, so the pytest floor is not raised.

setuptools is a build-system requirement, not a runtime dependency. The
PackageIndex fixes that still support Python >=3.9 land in 78.1.1. Later
setuptools advisories are fixed only in releases that require Python >=3.10.
"""

import json
import tomllib
import unittest
import urllib.request
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
            if version_ge(version, part[2:]) and version_key(version) != version_key(part[2:]):
                return False
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
        names.append(lower_bound(value)[0] if ">=" in value.split(";", 1)[0] else value.split(";", 1)[0].split("#", 1)[0].strip().lower())
    return names


def resolve(package, floor, python_version):
    request = urllib.request.Request(
        f"https://pypi.org/pypi/{package}/json",
        headers={"User-Agent": "thermal1d-dependency-floor-test"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        releases = json.loads(response.read().decode())["releases"]
    chosen = None
    chosen_python = None
    for version, files in releases.items():
        if not files or not version_ge(version, floor):
            continue
        if any(character.isalpha() for character in version):
            continue
        yanked = any(item.get("yanked") for item in files)
        if yanked:
            continue
        requires_python = files[0].get("requires_python")
        if not python_allows(requires_python, python_version):
            continue
        if chosen is None or version_ge(version, chosen) and version_key(version) != version_key(chosen):
            chosen = version
            chosen_python = requires_python
    if chosen is None:
        raise AssertionError(f"no {package}>={floor} release supports Python {python_version}")
    return chosen, chosen_python


class DependencyFloorTests(unittest.TestCase):
    def setUp(self):
        self.project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    def test_python_3_9_support_is_unchanged(self):
        requires_python = self.project["project"]["requires-python"]
        self.assertEqual(requires_python, ">=3.9")
        self.assertTrue(python_allows(requires_python, "3.9"))
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

    def test_pytest_remains_a_test_dependency_installable_on_python_3_9(self):
        test_extra = [lower_bound(item) for item in self.project["project"]["optional-dependencies"]["test"]]
        floors = dict(test_extra)
        self.assertIn("pytest", floors)
        self.assertNotIn("pytest", requirement_names(self.project["project"]["dependencies"]))
        requirement_floors = dict(
            lower_bound(line)
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.split("#", 1)[0].strip()
        )
        self.assertEqual(requirement_floors["pytest"], floors["pytest"])
        resolved, requires_python = resolve("pytest", floors["pytest"], "3.9")
        self.assertTrue(python_allows(requires_python, "3.9"), (resolved, requires_python))

    def test_setuptools_resolution_meets_floor_without_dropping_python_3_9(self):
        floor = dict(lower_bound(item) for item in self.project["build-system"]["requires"])["setuptools"]
        for python_version in ("3.9", "3.12"):
            resolved, requires_python = resolve("setuptools", floor, python_version)
            self.assertTrue(version_ge(resolved, "78.1.1"), (python_version, resolved))
            if python_version == "3.9":
                self.assertTrue(python_allows(requires_python, "3.9"), (resolved, requires_python))
                self.assertFalse(version_ge(resolved, "83.0.0"), (resolved, requires_python))


if __name__ == "__main__":
    unittest.main()
