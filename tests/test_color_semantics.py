"""Exercise semantic colors through verifier parsers and retained data checks."""
import importlib.util
from pathlib import Path
import re
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/document-diagrams/scripts'


def verifier(kind):
    spec = importlib.util.spec_from_file_location(kind, SCRIPTS / f'verify-{kind}.py')
    module = importlib.util.module_from_spec(spec)
    # Verifiers live in the installable skill, which must stay free of caches.
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


class ColorSemanticsTests(unittest.TestCase):
    def test_blue_bubbles_swarm_dots_and_segments_are_not_implicitly_focal(self):
        cases = {
            'bubble': ('<circle data-name="{i}" data-x="{i}" data-y="1" data-size="10" cx="{i}0" cy="30" r="4"', 'parse_bubbles', 'check_focal'),
            'beeswarm': ('<circle data-name="{i}" data-value="{i}" cx="{i}0" cy="30" r="4"', 'parse_dots', 'check_focal'),
            'marimekko': ('<rect data-column="{i}" data-segment="Input" data-amount="10" x="{i}0" y="30" width="10" height="20"', 'parse_segments', 'check_accent'),
        }
        for kind, (mark, parser, checker) in cases.items():
            module = verifier(kind)
            for focal_count in (0, 1, 2):
                with self.subTest(kind=kind, focal_count=focal_count):
                    source = '<svg>' + ''.join(
                        mark.format(i=i) + (' data-focal="true" stroke="#a855f7"' if i <= focal_count else ' stroke="#3b82f6"')
                        + ' fill="#dbeafe"/>' for i in (1, 2)) + '</svg>'
                    findings = []
                    document = source if kind == 'beeswarm' else module.parse_document(source)
                    marks = getattr(module, parser)(document, findings, 'colors.svg')
                    self.assertEqual(findings, [])
                    self.assertEqual(len(marks), 2)
                    self.assertEqual(sum(mark.accent for mark in marks), focal_count)
                    if kind == 'beeswarm':
                        getattr(module, checker)(marks, findings, source, 'colors.svg')
                    else:
                        getattr(module, checker)(marks, findings, 'colors.svg')
                    self.assertEqual(bool(findings), focal_count > 1)

    def test_semantic_blue_cannot_bypass_swarm_uniformity(self):
        module = verifier('beeswarm')
        source = '<svg>' + ''.join(
            f'<circle data-value="{i}" cx="{i * 20}" cy="30" r="4" stroke="#3b82f6" fill="{fill}"/>'
            for i, fill in enumerate(('#dbeafe', '#d1fae5'), 1)) + '</svg>'
        findings = []
        dots = module.parse_dots(source, findings, 'swarm.svg')
        module.check_ink(dots, findings, source, 'swarm.svg')
        self.assertTrue(any('one fill' in finding for finding in findings), findings)
        findings = []
        source = source.replace('#d1fae5', '#dbeafe')
        dots = module.parse_dots(source, findings, 'swarm.svg')
        module.check_ink(dots, findings, source, 'swarm.svg')
        self.assertEqual(findings, [])

    def test_series_focus_weights_follow_metadata_not_blue(self):
        for kind in ('bump', 'ridgeline'):
            with self.subTest(kind=kind):
                module = verifier(kind)
                if kind == 'bump':
                    mark = '<path data-series="{name}" data-ranks="1,2,3" d="M20,20 L40,40 L60,60"'
                else:
                    mark = '<path data-ridge="{name}" data-baseline="100" data-bins="0,1,2,3,3,2,1,0" d="M0,100 L10,99 L20,98 L30,97 L40,97 L50,98 L60,99 L70,100 Z"'
                source = '<svg>' + mark.format(name='Input') + ' stroke="#3b82f6" stroke-width="1.2"/>' + mark.format(name='Analysis') + ' stroke="#a855f7" stroke-width="2.4" data-focal="true"/></svg>'
                findings = []
                if kind == 'bump':
                    marks = module.parse_series(source, findings, 'series.svg')
                    check = lambda: module.check_focus(marks, findings, source, 'series.svg')
                else:
                    marks = module.parse_ridges(module.parse_document(source), findings, 'series.svg')
                    check = lambda: module.check_focus(marks, findings, 'series.svg')
                self.assertEqual(findings, [])
                self.assertEqual(len(marks), 2)
                self.assertEqual([mark.focal for mark in marks], [False, True])
                check()
                self.assertEqual(findings, [])
                marks[1].width = 1.2
                check()
                self.assertTrue(findings, 'a declared focus must retain the required weight')
                findings.clear()
                marks[1].width = 2.4
                marks[0].focal = True
                check()
                self.assertTrue(findings, 'two editorial foci must still fail')

    def test_blueprint_repeats_role_palette_without_extra_focus(self):
        module = verifier('service-blueprint')
        source = '<svg><g data-layer="backstage">' + ''.join(
            f'<rect data-stage="S{i}" data-name="N{i}" x="{i * 100}" y="100" width="80" height="40" fill="#dbeafe" stroke="#3b82f6" data-focal="{str(i == 1).lower()}"/>' for i in (1, 2)) + '</g></svg>'
        for two_foci in (False, True):
            current = source.replace('data-focal="false"', 'data-focal="true"') if two_foci else source
            findings, row_marks = [], []
            _, cells, _ = module.parse_marks(current, findings, row_marks)
            self.assertEqual(findings, [])
            self.assertEqual(len(cells), 2)
            module.check_focal(current, cells, row_marks, findings)
            self.assertEqual(bool(findings), two_foci)

    def test_waterfall_keeps_sign_fill_and_explicit_focus(self):
        module = verifier('waterfall')
        source = '<svg>' + ''.join(
            f'<rect data-role="delta" data-value="{value:+d}" data-name="{name}" x="{i * 80}" y="40" width="40" height="20" fill="{fill}" stroke="#3b82f6"/>'
            for i, (name, value, fill) in enumerate((('rise', 20, '#dbeafe'), ('fall', -10, '#ffffff')))) + '</svg>'
        findings = []
        bars = module.parse_bars(source, findings)
        self.assertEqual(findings, [])
        self.assertEqual(len(bars), 2)
        module.check_sign_treatment(bars, findings, '#ffffff')
        self.assertEqual(findings, [])
        bars[1].fill = '#dbeafe'
        module.check_sign_treatment(bars, findings, '#ffffff')
        self.assertTrue(findings, 'a semantic hue cannot hide a filled decrease')
        findings.clear()
        bars[1].fill = '#ffffff'
        current = source.replace('data-name="rise"', 'data-name="rise" data-focal="true"').replace('#3b82f6', '#a855f7')
        bars = module.parse_bars(current, findings)
        self.assertEqual([bar.focal for bar in bars], [True, False])
        module.check_sign_treatment(bars, findings, '#ffffff')
        self.assertEqual(findings, [])
        current = current.replace('data-name="fall"', 'data-name="fall" data-focal="true"')
        bars = module.parse_bars(current, findings)
        module.check_sign_treatment(bars, findings, '#ffffff')
        self.assertTrue(findings, 'semantic colors must not relax the focal count')

    def test_waterfall_outline_contrast_and_equivalent_white_paints(self):
        module = verifier('waterfall')
        for white in ('#ffffff', '#fff', 'white', 'rgb(255,255,255)'):
            for stroke in ('#3b82f6', '#b45309', '#166534', '#f59e0b', '#22c55e'):
                with self.subTest(white=white, stroke=stroke):
                    source = f'<rect data-role="delta" data-value="-10" x="20" y="20" width="40" height="20" fill="{white}" stroke="{stroke}"/>'
                    findings = []
                    bars = module.parse_bars(source, findings)
                    module.check_sign_treatment(bars, findings, '#ffffff')
                    if stroke in ('#f59e0b', '#22c55e'):
                        self.assertTrue(any('3:1' in f for f in findings), findings)
                    else:
                        self.assertEqual(findings, [])

    def test_copyable_bubble_example_declares_its_focus(self):
        reference = (SCRIPTS.parent / 'references/type-scatter.md').read_text()
        circles = re.findall(r'<circle\b(?=[^>]*data-size=)[^>]+>', reference)
        self.assertTrue(circles)
        source = '<svg>' + ''.join(circles).replace('{accent @ 0.15}', '#f3e8ff').replace('{accent}', '#a855f7') + '</svg>'
        module = verifier('bubble')
        findings = []
        bubbles = module.parse_bubbles(module.parse_document(source), findings, 'copied.svg')
        self.assertEqual(findings, [])
        self.assertEqual(sum(b.accent for b in bubbles), 1)

    def test_colored_waterfall_end_to_end_retains_conservation_and_carries(self):
        module = verifier('waterfall')
        source = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
        <rect width="400" height="240" fill="#ffffff"/>
        <rect data-role="total" data-value="100" x="60" y="100" width="40" height="100" fill="#dbeafe" stroke="#1e40af"/>
        <rect data-role="delta" data-value="+20" x="140" y="80" width="40" height="20" fill="#dbeafe" stroke="#1e40af"/>
        <rect data-role="delta" data-value="-10" x="220" y="80" width="40" height="10" fill="white" stroke="#1e40af"/>
        <rect data-role="total" data-value="110" x="300" y="90" width="40" height="110" fill="#dbeafe" stroke="#1e40af"/>
        <line data-carry="100" x1="100" x2="140" y1="100" y2="100"/>
        <line data-carry="120" x1="180" x2="220" y1="80" y2="80"/>
        <line data-carry="110" x1="260" x2="300" y1="90" y2="90"/>
        <text x="80" y="92" text-anchor="middle">100</text>
        <text x="160" y="72" text-anchor="middle">+20</text>
        <text x="240" y="102" text-anchor="middle">-10</text>
        <text x="320" y="82" text-anchor="middle">110</text>
        </svg>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'waterfall.svg'
            path.write_text(source)
            self.assertEqual(module.verify_file(path), [])
            for bad in (source.replace('data-value="110"', 'data-value="111"'),
                        source.replace('y1="80" y2="80"', 'y1="85" y2="85"'),
                        source.replace('fill="white"', 'fill="#dbeafe"')):
                path.write_text(bad)
                self.assertTrue(module.verify_file(path))


if __name__ == '__main__':
    unittest.main()
