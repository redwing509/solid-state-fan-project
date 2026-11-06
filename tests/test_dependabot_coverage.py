"""Dependabot entries must match first-party manifests that exist in the repo.

GitHub's pip updater covers requirements files and PEP 621 pyproject.toml
manifests. engines/thermal1d has both. The github-actions entry covers
.github/workflows.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "raw-cases", "results"}
MANIFEST_ECOSYSTEMS = {
    "requirements.txt": "pip",
    "pyproject.toml": "pip",
    "Pipfile": "pip",
    "package.json": "npm",
    "go.mod": "gomod",
    "Cargo.toml": "cargo",
    "pom.xml": "maven",
    "composer.json": "composer",
    "Gemfile": "bundler",
}


def parse_dependabot(text):
    entries = []
    current = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - package-ecosystem:"):
            if current:
                entries.append(current)
            value = line.split(":", 1)[1].strip().strip("\"'")
            current = {"package-ecosystem": value}
            continue
        if current is not None and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.strip()] = value.strip().strip("\"'")
    if current:
        entries.append(current)
    return entries


def first_party_manifests():
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.relative_to(ROOT).parts[0] in SKIP_DIRS:
            continue
        ecosystem = MANIFEST_ECOSYSTEMS.get(path.name)
        if ecosystem is None:
            continue
        if path.name == "pyproject.toml" and "[project]" not in path.read_text(encoding="utf-8"):
            continue
        found.append((ecosystem, path))
    return found


class DependabotCoverageTest(unittest.TestCase):
    def test_existing_actions_entry_is_preserved(self):
        entries = parse_dependabot((ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8"))
        ecosystems = [(item["package-ecosystem"], item["directory"]) for item in entries]
        self.assertIn(("github-actions", "/"), ecosystems)
        self.assertEqual(len(ecosystems), len(set(ecosystems)))
        workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
        self.assertTrue(workflows)

    def test_pip_entry_covers_thermal1d_manifests(self):
        thermal = ROOT / "engines" / "thermal1d"
        pyproject = (thermal / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[project]", pyproject)
        self.assertIn("dependencies", pyproject)
        requirement_lines = [
            line.split("#", 1)[0].strip()
            for line in (thermal / "requirements.txt").read_text(encoding="utf-8").splitlines()
        ]
        self.assertTrue(any(requirement_lines))

        entries = parse_dependabot((ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8"))
        pip_dirs = [item["directory"] for item in entries if item["package-ecosystem"] == "pip"]
        self.assertIn("/engines/thermal1d", pip_dirs)

    def test_every_first_party_manifest_has_an_entry(self):
        entries = parse_dependabot((ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8"))
        covered = {(item["package-ecosystem"], item["directory"]) for item in entries}
        missing = []
        for ecosystem, path in first_party_manifests():
            relative_dir = path.parent.relative_to(ROOT).as_posix()
            directory = "/" if relative_dir == "." else f"/{relative_dir}"
            if (ecosystem, directory) not in covered:
                missing.append(f"{ecosystem} {path.relative_to(ROOT)}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
