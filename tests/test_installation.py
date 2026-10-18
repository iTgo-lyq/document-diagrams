"""Exercise installation in isolation and catch accidental repository dependencies."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check import SKILL, check_installation


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.installed = self.root / "document-diagrams"
        shutil.copytree(SKILL, self.installed)

    def test_skill_works_without_repository_or_git(self):
        self.assertFalse((self.installed / ".git").exists())
        self.assertEqual(check_installation(self.installed), [])

    def test_reference_cannot_escape_even_when_target_exists(self):
        (self.root / "external.md").write_text("Outside the install", encoding="utf-8")
        (self.installed / "references" / "escape.md").write_text(
            "[dependency](../../external.md)", encoding="utf-8"
        )
        self.assertTrue(any("reference leaves skill directory" in error for error in check_installation(self.installed)))

    def test_missing_transitive_reference_is_detected(self):
        (self.installed / "references" / "diagram-types.md").write_text(
            "[details](missing.md)", encoding="utf-8"
        )
        self.assertTrue(any("missing reference" in error for error in check_installation(self.installed)))

    def test_missing_bare_svg_resource_is_detected(self):
        reference = self.installed / "references" / "example.md"
        reference.write_text("Write <file.svg> using `assets/template.svg`.", encoding="utf-8")
        self.assertEqual(check_installation(self.installed), [])
        reference.write_text("Copy the shipped `example-missing.svg`.", encoding="utf-8")
        self.assertTrue(any("missing SVG resource example-missing.svg" in error
                            for error in check_installation(self.installed)))
        reference.unlink()
        helper = self.installed / "scripts" / "example.py"
        helper.write_text('"""See the shipped example-missing.svg."""', encoding="utf-8")
        self.assertTrue(any("missing example resource example-missing.svg" in error
                            for error in check_installation(self.installed)))

    def test_source_text_is_not_in_skill_instructions(self):
        self.assertEqual(check_installation(self.installed), [])
        (self.installed / "references" / "source.md").write_text(
            "Load upstream/diagram-design before drawing.", encoding="utf-8"
        )
        self.assertTrue(any("repository README.md" in error for error in check_installation(self.installed)))

    def test_readme_is_not_shipped_with_the_skill(self):
        self.assertFalse((self.installed / "README.md").exists())
        (self.installed / "README.md").write_text("Repository documentation", encoding="utf-8")
        self.assertTrue(any("README belongs in the repository" in error for error in check_installation(self.installed)))

    def test_embedded_source_and_symlinks_are_rejected(self):
        (self.installed / "upstream").mkdir()
        (self.installed / "references" / "linked.md").symlink_to(ROOT / "README.md")
        errors = check_installation(self.installed)
        self.assertTrue(any("development dependency" in error for error in errors))
        self.assertTrue(any("symbolic links" in error for error in errors))

    def test_source_copy_is_complete_and_checks_outside_the_repository(self):
        expected = {path.relative_to(SKILL) for path in SKILL.rglob("*") if path.is_file()}
        installed = {path.relative_to(self.installed) for path in self.installed.rglob("*") if path.is_file()}
        self.assertEqual(installed, expected)
        for relative in expected:
            self.assertEqual((self.installed / relative).read_bytes(), (SKILL / relative).read_bytes())
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check.py"), "--skill-dir", str(self.installed)],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
