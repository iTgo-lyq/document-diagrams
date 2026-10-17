"""Validate shipped templates and helpers in an isolated installation."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/document-diagrams'


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.skill = self.work / 'installed'
        shutil.copytree(SKILL, self.skill)

    def run_helper(self, name, *args):
        result = subprocess.run(
            [sys.executable, str(self.skill / 'scripts' / name), *map(str, args)],
            cwd=self.work, text=True, capture_output=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_all_types_are_routed_and_script_references_resolve(self):
        types = {p.name for p in (self.skill / 'references').glob('type-*.md')}
        self.assertEqual(len(types), 45)
        entry = (self.skill / 'SKILL.md').read_text()
        self.assertEqual(set(re.findall(r'\(references/(type-[\w-]+\.md)\)', entry)), types)
        for document in [self.skill / 'SKILL.md', *(self.skill / 'references').glob('*.md')]:
            for script in re.findall(r'(?<![\w/])scripts/([\w-]+\.py)', document.read_text()):
                self.assertTrue((self.skill / 'scripts' / script).is_file(), f'{document.name}: {script}')

    def test_svg_template_is_accessible_and_has_valid_geometry(self):
        template = self.skill / 'assets/template.svg'
        self.run_helper('check_svg.py', template)
        self.run_helper('verify-geometry.py', template)
        root = ET.fromstring(template.read_text())
        self.assertEqual(root.attrib['role'], 'img')
        self.assertIn('Noto Sans CJK SC', template.read_text())

    def test_output_resources_are_svg_only(self):
        self.assertEqual([p.name for p in (self.skill / 'assets').iterdir()], ['template.svg'])
        for name in ['export_svg.py', 'export_png.py', 'self_check.py', 'verify-motion.py']:
            self.assertFalse((self.skill / 'scripts' / name).exists())
        for name in ['animation.md', 'export.md', 'export-registry.md']:
            self.assertFalse((self.skill / 'references' / name).exists())
        for document in [self.skill / 'SKILL.md', *(self.skill / 'references').glob('*.md')]:
            self.assertNotIn('<foreignObject', document.read_text(), document.name)

    def test_svg_check_rejects_broken_naming_and_resource_references(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('svg_check', self.skill / 'scripts/check_svg.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = (self.skill / 'assets/template.svg').read_text()
        for bad in [source.replace('aria-labelledby="diagram-title diagram-desc"', 'aria-labelledby="missing"'),
                    source.replace('url(#diagram-arrow)', 'url(#missing)'),
                    source.replace('url(#diagram-arrow)', 'url(https://example.invalid/a.svg)'),
                    source.replace('</svg>', '<script>alert(1)</script></svg>'),
                    '<html><body>not SVG</body></html>']:
            path = self.work / 'bad.svg'
            path.write_text(bad)
            self.assertTrue(module.check(path))

    def test_dumbbell_domain_and_actual_palette_contract(self):
        self.run_helper('verify-dumbbell.py')

    def test_template_arrows_clear_source_and_target(self):
        root = ET.parse(self.skill / 'assets/template.svg').getroot()
        marker = next(e for e in root.iter() if e.tag.endswith('marker'))
        self.assertEqual(marker.get('markerUnits'), 'userSpaceOnUse')
        extension = 8 - float(marker.get('refX'))
        paths = [e.get('d') for e in root.iter() if e.get('marker-end')]
        for path, source, target in zip(paths, [280, 580], [380, 680]):
            coords = list(map(float, re.findall(r'\d+(?:\.\d+)?', path)))
            self.assertEqual(coords[0] - source, 5)
            self.assertEqual(target - coords[-1] - extension, 5)
        self.assertEqual(len(paths), 2)

    def test_mermaid_preserves_decision_labels_and_return_path(self):
        source = self.work / 'flow.mmd'
        source.write_text('flowchart LR\n A[Request] --> B{Valid?}\n B -->|yes| C[Store]\n B -.->|no| A\n')
        data = json.loads(self.run_helper('mermaid_extract.py', source, '--json'))
        diagram = data['diagrams'][0]
        self.assertEqual(len(diagram['nodes']), 3)
        self.assertEqual(len(diagram['edges']), 3)
        self.assertIn('yes', json.dumps(diagram))
        self.assertIn('no', json.dumps(diagram))


if __name__ == '__main__':
    unittest.main()
