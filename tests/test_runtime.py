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

    def test_heatmap_enforces_the_blue_focal_budget(self):
        source = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
        <rect width="100%" height="100%" fill="#ffffff"/>
        <text data-row-label="R" x="10" y="80">R</text>
        <text data-col="C1" x="100" y="30">C1</text>
        <text data-col="C2" x="220" y="30">C2</text>
        <rect data-row="R" data-col="C1" data-value="1" x="60" y="50" width="100" height="60" fill="rgba(30,41,59,0.1)"/>
        <rect data-row="R" data-col="C2" data-value="2" data-focal="true" x="180" y="50" width="100" height="60" fill="rgba(59,130,246,0.2)"/>
        </svg>'''
        path = self.work / 'heatmap.svg'
        path.write_text(source)
        self.run_helper('verify-heatmap.py', path)
        for bad, message in [
                (source.replace('rgba(30,41,59,0.1)', 'rgba(59,130,246,0.1)'), 'found 2 focal cells'),
                (source.replace(' data-focal="true"', ''), 'accent fill requires data-focal=true'),
                (source.replace('rgba(59,130,246,0.2)', 'rgba(234,88,12,0.85)'), 'require accent blue RGB'),
                (source.replace('rgba(30,41,59,0.1)', 'rgba(37,99,235,0.3)'), 'require ink RGB')]:
            with self.subTest(message=message):
                path.write_text(bad)
                result = subprocess.run(
                    [sys.executable, str(self.skill / 'scripts/verify-heatmap.py'), str(path)],
                    cwd=self.work, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(message, result.stdout + result.stderr)

    def test_polar_validates_standalone_svg_and_data_geometry(self):
        source = (ROOT / 'tests/fixtures/polar-static.svg').read_text()
        path = self.work / 'polar.svg'
        path.write_text(source)
        self.run_helper('check_svg.py', path)
        self.run_helper('verify-polar.py', path)
        for bad, message in [
                (source.replace('data-polar-value="32"', 'data-polar-value="80"', 1), 'linear endpoint outside tolerance'),
                (source.replace('</svg>', '<style>@import url(https://fonts.googleapis.com/css2);</style></svg>'),
                 'CSS stylesheet loading is forbidden')]:
            path.write_text(bad)
            result = subprocess.run(
                [sys.executable, str(self.skill / 'scripts/verify-polar.py'), str(path)],
                cwd=self.work, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(message, result.stdout + result.stderr)

    def test_processing_instructions_cannot_load_external_styles(self):
        source = (ROOT / 'tests/fixtures/polar-static.svg').read_text()
        instruction = '<?xml-stylesheet type="text/css" href="https://example.invalid/external.css"?>'
        path = self.work / 'polar.svg'
        for helper in ['check_svg.py', 'verify-polar.py']:
            for valid in ['<?xml version="1.0"?>\n' + source,
                          source.replace('</svg>', '<!-- ' + instruction + ' --></svg>')]:
                path.write_text(valid)
                self.run_helper(helper, path)
            for bad in [instruction + source, source + instruction,
                        source.replace('</svg>', instruction + '</svg>')]:
                with self.subTest(helper=helper, position=bad.index(instruction)):
                    path.write_text(bad)
                    result = subprocess.run(
                        [sys.executable, str(self.skill / 'scripts' / helper), str(path)],
                        cwd=self.work, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn('processing instructions', result.stdout + result.stderr)

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

    def test_delta_accepts_filled_marker_clearance_in_each_direction(self):
        source = (ROOT / 'tests/fixtures/delta-clearance.svg').read_text()
        horizontal = source.replace('x="40" y="120"', 'x="200" y="40"').replace('M 80 85 V 109', 'M 125 60 H 189')
        reverse = lambda s: s.replace('data-from="api" data-to="store"', 'data-from="store" data-to="api"')
        variants = [source, horizontal,
                    reverse(source).replace('M 80 85 V 109', 'M 80 115 V 91'),
                    reverse(horizontal).replace('M 125 60 H 189', 'M 195 60 H 131')]
        for index, variant in enumerate(variants):
            with self.subTest(direction=index):
                path = self.work / 'delta.svg'
                path.write_text(variant)
                self.run_helper('check_svg.py', path)
                self.run_helper('verify-architecture-delta.py', path)

    def test_delta_rejects_wrong_endpoint_clearance_or_direction(self):
        source = (ROOT / 'tests/fixtures/delta-clearance.svg').read_text()
        for route in ['M 80 80 V 120', 'M 80 75 V 131',
                      'M 80 85 H 100 V 109 H 80', 'M 140 85 V 109',
                      'M 39 60 V 109 H 80', 'M 80 85 H 39 V 140']:
            with self.subTest(route=route):
                path = self.work / 'delta.svg'
                path.write_text(source.replace('M 80 85 V 109', route))
                result = subprocess.run(
                    [sys.executable, str(self.skill / 'scripts/verify-architecture-delta.py'), str(path)],
                    cwd=self.work, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn('clearance/tangent', result.stdout + result.stderr)

    def test_delta_requires_the_marker_assumed_by_its_clearance(self):
        source = (ROOT / 'tests/fixtures/delta-clearance.svg').read_text()
        marker = 'marker-end="url(#delta-arrow)"'
        variants = [
            (source.replace(marker, ''), 'defined canonical filled marker-end'),
            (source.replace(marker, 'marker-end="url(#missing)"'), 'defined canonical filled marker-end'),
            (source.replace(marker, marker + ' marker-start="url(#delta-arrow)"'), 'only an end marker'),
            (source.replace('refX="2"', 'refX="8"'), 'defined canonical filled marker-end'),
            (source.replace('L2,4 z', 'L4,4 z'), 'defined canonical filled marker-end'),
            (source.replace(marker, marker + ' style="marker-end:none"'), 'CSS geometry overrides'),
        ]
        path = self.work / 'delta.svg'
        for bad, message in variants:
            with self.subTest(message=message):
                path.write_text(bad)
                result = subprocess.run(
                    [sys.executable, str(self.skill / 'scripts/verify-architecture-delta.py'), str(path)],
                    cwd=self.work, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(message, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
