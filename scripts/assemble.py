#!/usr/bin/env python3
"""Assemble the standalone instructions from the pinned reference sources.

The retention/replacement boundary is documented in the repository README.
This maintainer tool is never included in the installed skill.
"""
from pathlib import Path
import re
import shutil
from semantic_colors import guidance as color_guidance
from semantic_colors import verifier as color_verifier

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'upstream/diagram-design/skills/diagram-design'
OUT = ROOT / 'skills/document-diagrams'
FONT = "'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-serif"
COLORS = {
    '#f5f5f5': '#ffffff', '#2d3142': '#1e293b', '#4f5d75': '#64748b',
    '#bf4520': '#3b82f6', '#ff6b4a': '#3b82f6', '#e8603c': '#3b82f6',
    '#f5f2ec': '#ffffff', '#faf8f5': '#ffffff', '#f7f4ee': '#ffffff',
    '#2e5aa8': '#3b82f6', '#b85450': '#ec4899', '#4e7a60': '#22c55e',
    '#6c8b6a': '#22c55e', '#a56c27': '#f59e0b', '#7c5c91': '#a855f7',
    '#5a7d9a': '#3b82f6', '#7a8c47': '#22c55e', '#c9a23a': '#f59e0b',
    '#7c8f6f': '#22c55e', '#5e7a9b': '#3b82f6', '#b8915a': '#f59e0b',
    '#9c6b50': '#ec4899', '#6e6479': '#a855f7',
    '#5a6580': '#64748b', '#4a7c59': '#22c55e',
}


def sections(text):
    """Find real Markdown headings, ignoring code blocks."""
    items = []
    offset = 0
    fence = None
    for line in text.splitlines(keepends=True):
        mark = re.match(r'^\s*(`{3,}|~{3,})', line)
        if mark:
            if fence is None:
                fence = mark.group(1)[0]
            elif mark.group(1)[0] == fence:
                fence = None
        elif fence is None:
            heading = re.match(r'^(#{1,6}) (.+)', line)
            if heading:
                items.append((offset, len(heading.group(1)), heading.group(2).strip()))
        offset += len(line)
    return items


def replace_sections(text, matcher, replacement=''):
    edits = []
    headings = sections(text)
    for i, (start, level, title) in enumerate(headings):
        if not matcher(title):
            continue
        end = next((pos for pos, other, _ in headings[i+1:] if other <= level), len(text))
        if any(a <= start < b for a, b, _ in edits):
            continue
        value = replacement(title) if callable(replacement) else replacement
        edits.append((start, end, value))
    for start, end, value in reversed(edits):
        text = text[:start] + value + text[end:]
    return text


def marker(match):
    opening, body = match.group(1), match.group(2)
    if 'open' in opening or '<polyline' in body:
        return match.group(0)  # Open markers encode asynchronous semantics.
    ident = re.search(r'\bid="([^"]+)"', opening)
    if not ident:
        return match.group(0)
    paint = re.search(r'fill="([^"]+)"', body)
    color = paint.group(1) if paint else '{muted}'
    return (f'<marker id="{ident.group(1)}" markerWidth="8" markerHeight="8" '
            'refX="2" refY="4" orient="auto" markerUnits="userSpaceOnUse">'
            f'<path d="M0,0 L8,4 L0,8 L2,4 z" fill="{color}"/></marker>')


def visual_tokens(text):
    for old, new in COLORS.items():
        text = re.sub(re.escape(old), new, text, flags=re.I)
    text = re.sub(r'rgba?\(45,\s*49,\s*66', lambda m: m.group(0).replace('45', '30').replace('49', '41').replace('66', '59'), text)
    text = re.sub(r'rgba?\(191,\s*69,\s*32', lambda m: m.group(0).replace('191', '59').replace('69', '130').replace('32', '246'), text)
    text = re.sub(r'\b[Cc]oral\b', 'accent', text)
    text = re.sub(r'\bGeist Mono\b', 'system monospace', text)
    text = re.sub(r'\bGeist\b', 'system sans', text)
    text = re.sub(r'\bInstrument Serif\b', 'system sans', text)
    text = text.replace('JetBrains Mono', 'a blanket monospace face')
    text = re.sub(r'font-family="[^"]+"', f'font-family="{FONT}"', text)
    def size(m):
        value = float(m.group(1))
        return 'font-size="{' + ('title-size' if value >= 24 else 'node-size' if value >= 12 else 'secondary-size') + '}"'
    text = re.sub(r'font-size="(\d+(?:\.\d+)?)"', size, text)
    text = re.sub(r'font-style="italic"', '', text)
    text = re.sub(r'<marker\b([^>]+)>(.*?)</marker>', marker, text, flags=re.S)
    return text


def common(text):
    text = text.replace('diagram-design', 'document-diagrams').replace('Diagram Design', 'Document Diagrams')
    text = re.sub(r'style-guide\.md(?:#[\w-]+)?', 'visual-style.md', text)
    text = text.replace('<repo-root>', '<skill-dir>')
    text = text.replace('From a repository checkout, ', 'From the skill directory, ')
    text = text.replace('from a repository checkout', 'from the skill directory')
    text = re.sub(r'^.*(?:Dark mode:|Dark mode —|\*\*Dark mode\*\*:).*(?:\n|$)', '', text, flags=re.M)
    text = re.sub(r'\([^\n]*\[primitive-sketchy\.md\][^\n]*\)', '', text)
    text = text.replace('dark mode', 'the default palette').replace('light/dark', 'light')
    text = re.sub(r'\b(?:mono uppercase|uppercase mono|italic-serif|italic serif)\b', 'secondary', text, flags=re.I)
    text = text.replace('14 characters max, all caps, centered on its segment', 'short and centered on its segment')
    text = re.sub(r'^dark: false\n', '', text, flags=re.M)
    text = re.sub(r'^.*\*\*Dark theme\.\*\*.*\n', '', text, flags=re.M)
    text = re.sub(r'^.*Dark variant:.*\n', '', text, flags=re.M)
    text = re.sub(r'^- In the default palette,.*\n', '', text, flags=re.M)
    text = re.sub(r'\s*\((?:dark:|[^()\n]*in dark)[^()\n]*\)', '', text)
    text = text.replace('`paper` in light mode and `ink` in the default palette', '`paper`')
    text = text.replace('dark-mode token swap', 'visual token selection')
    text = text.replace('minimal light, minimal dark, and full-editorial examples', 'the white-background visual palette')
    text = text.replace('(`loop`, `loop-dark`, `loop-full`)', '(`loop`, `loop-detail`, `loop-overview`)')
    text = text.replace('so a light figure next to its `-dark` twin', 'so two figures next to each other')
    # Retain data-code meanings and face geometry while dropping dark palette columns.
    rows = text.splitlines()
    drop = []
    for i, row in enumerate(rows):
        if not row.startswith('|'):
            drop = []
            continue
        cells = [c.strip() for c in row.strip('|').split('|')]
        if any(re.fullmatch(r'(?:Color \()?Dark\)?', c, re.I) for c in cells):
            drop = [j for j, c in enumerate(cells) if re.fullmatch(r'(?:Color \()?Dark\)?', c, re.I)]
        if drop:
            rows[i] = '| ' + ' | '.join(c for j, c in enumerate(cells) if j not in drop) + ' |'
    text = '\n'.join(rows) + '\n'
    text = text.replace('— never hand-authored', '')
    return visual_tokens(text)


def write(relative, content):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.md':
        content = color_guidance(path.name, content)
        content = '\n'.join(line.rstrip() for line in content.splitlines())
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def adapt_reference(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'Decorative-only SVG[^\n]*', 'Decorative-only SVG carries `aria-hidden="true"` instead.', text)
    text = re.sub(r'^.*?`python3 scripts/(verify-[\w-]+\.py)[^\n]*scripts/test-[^\n]*$', r'Run `python3 scripts/\1 path/to/diagram.svg` to check the diagram metadata and geometry.', text, flags=re.M)
    # Style variants and example galleries are presentation assets, not type grammars.
    text = replace_sections(text, lambda h: bool(re.search(r'^(?:\d+(?:\.\d+)*\.?\s+)?(?:Dark(?: mode| variant)?|Examples|Summary Card Pattern|Page layout|Registered legacy sizes|Non-Latin labels)\b', h, re.I)))
    text = replace_sections(text, lambda h: bool(re.search(r'(?:Component color override|Color overrides|Recommended palette|Semantic palette|Type ramp per size class)', h, re.I)),
        lambda h: '## ' + h.split(' ', 1)[0] + ' Visual values\n\nUse [visual-style.md](visual-style.md) for colors, fonts, sizes and markers. Optional color inputs select a semantic palette; they do not change node roles, relationship kinds or layout formulas.\n\n')
    text = re.sub(r'^.*(?:assets/(?:example-|index\.html|icons\.html)|scripts/(?:test-|lint-skin|lint-render|verify-docs-sync|verify-screenshot|verify-skin)).*(?:\n|$)', '', text, flags=re.M)
    # Structural verifiers are included in the installed directory.
    text = re.sub(r'```(?:bash)?\n\s*```', '', text)
    text = re.sub(r'\[(.*?)\]\(assets/[^)]+\)', r'\1', text)
    text = text.replace('SKILL.md §5', 'visual-style.md').replace('skin linter', 'self-check')
    text = common(text)
    # Skin-specific family/weight language cannot remain as an instruction.
    text = re.sub(r'^.*(?:Italic \+ serif|Don.t substitute italic|Italic sans or italic mono|never as a blanket|sans/mono body).*(?:\n|$)', '', text, flags=re.M)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def finish_guidance(text):
    """Remove presentation literals without deleting the surrounding semantics."""
    text = re.sub(r'^.*(?:Dot pattern:|Dotted paper:).*\n', '', text, flags=re.M)
    text = text.replace(', and the 22×22 dot-pattern', '')
    text = re.sub(r'\bmono\b', 'system-font', text)
    text = text.replace('must be system-font', 'uses the secondary text role')
    text = text.replace('the editorial skin or any user-onboarded brand palette', 'the shared visual palette')
    text = text.replace('the active skin', 'the visual palette').replace('skin tokens', 'visual tokens')
    text = text.replace('default light skin', 'white background')
    text = re.sub(r' \(dark: `rgba\([^`]+`\)', '', text)
    text = text.replace('in both themes', 'against the actual background')
    text = text.replace('in light mode, `band-2` / `band-3` in dark', '')
    text = text.replace('`rule-solid` light or `soft` dark', '`rule-solid`')
    text = text.replace(' (`ink @ 0.40` on dark)', '')
    text = text.replace('survives both skins; "darkest" ships false on one of them', 'describes the opacity encoding without implying a different variable')
    text = text.replace('even the sketchy variant starts from a clean layout', 'start from a clean layout')
    text = re.sub(r'\(A brand.s onboarded palette.*?introduced\.\)', 'Other CSS color notations such as hsl() are outside this presentation-attribute pass.', text)
    text = re.sub(r'\s*letter-spacing="[^"]*"', '', text)
    text = re.sub(r'`?letter-spacing[=: ]+`?[\d.]+em`?', 'normal letter spacing', text)
    text = re.sub(r'tracked\s+`?[\d.]+em`?', 'normally spaced', text)
    # A role determines text size, independently of geometric pixel distances.
    def role_size(m):
        return m.group(1) + ('12px' if 'node-name' in m.group(1) else '10px')
    text = re.sub(r'(`(?:node-name|sublabel|eyebrow|arrow-label|callout)`(?:-role| role)?(?: at|,)?\s*\(?)[\d.]+(?:[–/][\d.]+)?\s*px', role_size, text)
    text = re.sub(r'font-size\s*[=: ]\s*\d+(?:\.\d+)?(?:\s*-?px)?', 'font-size=10', text)
    text = re.sub(r'(?m)^(title\s+.*)font-size=10', r'\1font-size=12', text)
    text = re.sub(r'(?m)^((?:tool|sub|in→out)\s+.*)\bsoft\b', r'\1muted', text)
    text = re.sub(r'(?<= at )\d+(?:\.\d+)?\s*px(?=, weight)', '10px', text)
    text = re.sub(r'size \d+(?:\.\d+)? (?:sans|system-font)', 'size 12 system-font', text)
    text = re.sub(r'\d+(?:\.\d+)?-px system-font text', '10px system-font text', text)
    text = text.replace('same pair at 11px/9px', 'same 12px/10px pair')
    text = text.replace('3-letter system-font abbreviation', 'short abbreviation')
    # Muted is the text role. Soft is a decorative line color with insufficient text contrast.
    text = text.replace('fill="{soft}"', 'fill="{muted}"')
    text = re.sub(r'(?m)^(- \*\*Zone label:).*$', '- **Zone labels:** use `muted` text on the white or group background. Keep the label readable at the secondary size; a translucent border color is not a text color.', text)
    text = re.sub(r'(?m)^- \*\*Every bubble keeps.*$', '- **Every bubble keeps a `muted` stroke.** The faint fill is not a boundary: measure the stroke against the actual background and keep it at least 3:1. Focal hue, labels and geometry provide redundant identification.', text)
    text = re.sub(r'(?m)^- \*\*Be honest about what that leaves.*$', '- **Contrast and redundancy:** a heavier stroke does not improve its contrast ratio. Verify the actual stroke/background pair at 3:1 and text/background at 4.5:1; retain position, endpoint labels, legend and stroke weight as redundant cues.', text)
    text = re.sub(r'(?m)^- \*\*Labels stay `ink`.*$', '- **Labels stay `ink` (names) and `muted` (values), including focal series.** Accent strokes are not text colors; measure the actual contrast.', text)
    text = re.sub(r'\(0\.55 gives 3\.19:1; the 0\.25 the axis uses gives 1\.60:1\)', '(verify the actual composited color rather than reusing a ratio from another palette)', text)
    text = text.replace('default accent passes AA as text (4.71:1)', 'accent is reserved for graphical emphasis')
    text = re.sub(r'that is where an `ink` stroke crosses 3:1.*?every line in this figure is data, not decoration\.', 'measure the composited ink against white and keep every data line at least 3:1.', text)
    text = text.replace('(3.84:1)', '(verify its contrast)').replace('(3.48:1 on paper)', '(a decorative line role)')
    text = text.replace('rust-red', 'pink').replace('custom olive', 'data green').replace('slate-blue', 'blue')
    text = text.replace('container fill `rgba(122,140,71,0.06)`, stroke `rgba(122,140,71,0.45)`, name text `#22c55e`', 'container fill `#d1fae5`, stroke `#22c55e`, name text `#166534`')
    text = re.sub(r'<text\b([^>]*?)fill="(?:\{accent\}|#3b82f6)"', r'<text\1fill="{ink}"', text)
    text = text.replace('Title text in `accent`.', 'Title text in `ink`.')
    text = text.replace('Focal bar label in `accent`; others in `muted`.', 'Focal bar label in `ink`; others in `muted`.')
    text = text.replace("the focal bar's label may take accent", "the focal bar's label uses `ink`")
    text = text.replace('Corner tag in `accent`, weight 600.', 'Corner tag in `ink`, weight 600.')
    text = text.replace('`muted` (or `accent` on focal)', '`muted` (or `ink` on focal)')
    text = text.replace('station name may use `accent`', 'station name uses the dark semantic text color')
    text = text.replace('even though the accent fill is not — see below', 'with contrast measured against the actual background — see below')
    for old, new in [('`#22c55e` sage', '`#22c55e` green'), ('`#3b82f6` dusty-blue', '`#3b82f6` blue'),
                     ('`#f59e0b` mustard', '`#f59e0b` orange'), ('`#ec4899` rust-brown', '`#ec4899` pink'),
                     ('`#a855f7` slate', '`#a855f7` purple'), ('`out: TB` mustard chip', '`out: TB` orange chip')]:
        text = text.replace(old, new)
    text = re.sub(r'^Text inside chip: white[^\n]*', 'For each chip hue, use the matching light fill, stroke and dark text triple from visual-style.md. Keep the code visible at 10px semibold. The hue encodes payload format according to this table.', text, flags=re.M)
    text = re.sub(r'`scripts/build-exploded-examples\.py`[^\n]*', '`scripts/axonometry.py` supplies the projection helpers below.', text)
    text = re.sub(r'`scripts/build-axonometric-plan-examples\.py`[^\n]*', '`scripts/axonometry.py` supplies the shared projection helpers.', text)
    text = text.replace('`<skill-dir>` is `skills/document-diagrams/` in this repo, or the skill\'s own directory when it\'s installed standalone or as a plugin.', '`<skill-dir>` is this installed skill directory.')
    text = re.sub(r'\bCreate branded ', 'Create ', text)
    text = text.replace(', and onboarding guidance', '')
    text = text.replace('an light visual system', 'a light visual system')
    text = text.replace('the **phase-band palette** (§6.1)', 'the **phase-band palette** in visual-style.md')
    text = text.replace('same phase-band palette as the horizontals, §6.1', 'same phase-band palette as the horizontals')
    text = text.replace('header, diagram, summary cards, footer, live fonts', 'header, diagram, optional context, local system fonts')
    text = text.replace('page overflow, an unreachable clipped SVG, a missing local scroller, or a\n', '')
    text = text.replace('system monospace 8px', 'secondary CJK system text at 10px')
    text = text.replace(' (or 7px for tight layouts)', '')
    lines = []
    for line in text.splitlines():
        # Casing of machine-readable change words and abstract-class notation
        # carry semantics; decorative label typography does not.
        semantic_case = any(s in line for s in ['uppercase change word', 'same uppercase word', 'Uppercase names (`X`'])
        if not semantic_case:
            line = line.replace('both lines uppercase', 'both lines in the secondary text role')
            line = line.replace('(uppercased)', '(preserving the supplied label)')
            line = re.sub(r'\b(?:all uppercase|uppercase|tracked|small-caps)(?:,? )?', '', line)
            line = re.sub(r'\s+tracked(?=[.,])', '', line)
        if 'abstract class' not in line:
            line = line.replace('"italic pointer"', '"annotation pointer"')
            line = re.sub(r'\b[Ii]talic ', '', line)
        line = re.sub(r',\s*\.', '.', line)
        line = re.sub(r'(?<=px) +\.', '.', line)
        lines.append(line)
    text = '\n'.join(lines) + '\n'
    for extension in ['html', 'svg']:
        text = text.replace(f'the moving component in `example-wardley.{extension}`', 'a moving component')
        text = text.replace(f' — which is also what `example-line.{extension}` actually ships, the parent prose being stale on this point', '')
        text = text.replace(f'A fresh generation from this YAML produces a diagram visually indistinguishable from the shipped `example-dp-security-matrix.{extension}`.', 'Generate the SVG directly from this YAML using the layout formulas and shared visual specification.')
    text = re.sub(r'Worked YAML — full inputs for `example-[\w-]+\.(?:html|svg)`', 'Worked YAML — complete inputs', text)
    text = re.sub(r'The YAML in §1 is the \*\*complete\*\* inputs definition for the shipped `example-medallion\.(?:html|svg)`\..*?(?=\n|$)', 'The YAML in §1 is the **complete** input definition. Derive coordinates from §2 and retain these inputs in an XML comment in the generated SVG for reproducibility.', text)
    text = text.replace('**Static fallback:**', '**Static composition:**')
    text = text.replace('animation that changes item order', 'reordered items')
    text = text.replace('typing animation as the only readable copy', 'missing or partial readable copy')
    text = re.sub(r"This pattern has no animated form.*?Every ID badge", 'Every ID badge', text)
    text = text.replace('The complete inputs that map to the shipped canonical example.', 'Complete inputs for generating an SVG from this section.')
    text = text.replace('A shipped treemap once had its smallest cell drawn 50% oversized with every gate green for exactly this reason.', 'A small cell can be drawn 50% oversized while label-only checks pass for exactly this reason.')
    text = text.replace('shipped grammar', 'supported grammar').replace('shipped diagram', 'finished diagram')
    text = text.replace('shipped', 'illustrative')
    return text


def icon_guidance():
    """Keep the semantic registry; do not redistribute the old visual icon set."""
    source = (BASE / 'references/primitive-icons.md').read_text()
    lines = ['# Icon roles', '',
             'An icon is optional and never replaces the component name, role, or relationship. '
             'Use a small generic outline drawn from basic SVG shapes in a 24×24 slot; '
             'use the shared stroke/text colors and keep the visible component label. '
             'Product names can be labels instead of logos. Do not fetch or embed external images.', '',
             'The following identifiers are accepted in type inputs. Preserve their meaning when importing; '
             'if there is no suitable local symbol, use a labeled box. Decorative symbols carry `aria-hidden="true"`.', '']
    for _, level, title in sections(source):
        if level == 2 and title not in {'Usage', 'License attribution'}:
            lines += ['## ' + title, '']
        elif level == 3:
            lines.append('- `' + title + '`')
    return '\n'.join(lines)


def svg_scope(text):
    text = replace_sections(text, lambda h: h in {'Optional motion', 'Exporting to PNG / SVG'}, '')
    text = re.sub(r'Use \[`references/animation\.md`\][^\n]*', '', text)
    text = re.sub(r'^- Optional animation[^\n]*\n', '', text, flags=re.M)
    text = re.sub(r'^.*(?:\[animation\.md\]|template-motion|\| Max motion|If animated,|Optional explanatory motion).*(?:\n|$)', '', text, flags=re.M)
    text = text.replace(', and the motion limits', '')
    text = text.replace('HTML/SVG/PNG', 'SVG')
    text = text.replace('as self-contained HTML files with inline SVG', 'as self-contained SVG files')
    text = text.replace('Public HTML metadata contract', 'SVG metadata contract')
    text = text.replace('format, size, detail level, and audience', 'size, detail level, and audience')
    text = text.replace('format, size, detail level, audience', 'size, detail level, audience')
    text = text.replace('four dials', 'three dials').replace('four import decisions', 'three import decisions')
    text = text.replace('; when animation is chosen, load `animation.md`', '')
    text = text.replace('at the format, size, and detail level the destination needs', 'as SVG at the size and detail level the destination needs')
    text = text.replace('Set `--format`, `--size`, `--detail`, and `--audience`', 'Set size, detail and audience')
    text = re.sub(r'^Command-level flags are[^\n]*', 'These are authoring decisions. Use only the extraction flags listed in the helper command above.', text, flags=re.M)
    text = text.replace('top-of-file HTML comment', 'top-of-file XML comment')
    text = re.sub(r'^\| \*\*Format\*\*.*\n', '', text, flags=re.M)
    text = text.replace('self_check.py', 'check_svg.py')
    text = text.replace('Accessible-SVG contract, single-file safety, content inside the viewBox, motion basics.', 'XML syntax, accessible naming, unique IDs and local resource references; inspect geometry and rendered bounds separately.')
    text = text.replace('Complete static/no-JS', 'Complete static')
    text = re.sub(r'^- \[ \] (?:\*\*)?`min-width` equals.*\n', '- [ ] SVG dimensions preserve readable text at the intended display size, with all content inside the viewBox?\n', text, flags=re.M)
    text = re.sub(r'^- \[ \] `@media print`.*\n', '', text, flags=re.M)
    text = re.sub(r'^- \*\*Responsive presentation:\*\*.*$', '- **Display size:** preserve the three-panel comparison at a readable width. Do not compress labels or scale snapshots independently. Keep the complete comparison in the SVG viewBox.', text, flags=re.M)
    text = text.replace('roughly the page `<h1>`, ', '')
    text = text.replace('roughly the page `<h1>`, and ', '')
    text = text.replace('Only the page `<h1>` uses `title`.', 'Only the overall SVG heading uses the 16px `title` role.')
    text = re.sub(r', or the `/document-diagrams:[^`]+` slash command', '', text)
    text = re.sub(r', or uses `/document-diagrams:[^`]+`', '', text)
    text = text.replace('and the matching import command', 'and requests to import these formats')
    text = re.sub(r'^3\. (?:Produce `svg` / `png`|Export SVG/PNG|Export SVG or PNG)[^\n]*\n', '3. Validate the SVG and inspect the rendered result.\n', text, flags=re.M)
    text = text.replace('Write the self-contained HTML.', 'Write the self-contained SVG directly.')
    text = text.replace('one HTML file per page', 'one SVG file per page')
    text = text.replace('HTML file', 'SVG file').replace('.html', '.svg')
    text = text.replace('No OCL', 'No OCL')
    text = text.replace('and, for anything longer than a short phrase, in the sidecar registry (see `export-registry.md`)', 'with full values kept in these attributes')
    text = text.replace('the sidecar registry is the layer that reassembles the full graph across files', 'stable metadata IDs allow the graph to be traced across files')
    text = text.replace('the registry', 'the embedded metadata')
    text = text.replace('(see ADR 0001)', '')
    text = text.replace('Color, motion, and position', 'Color and position')
    return text


def delta_clearance(text):
    """Keep endpoint identity checks while adapting the filled-arrow clearance."""
    helper = '''def endpoint_meets_port(points, bounds, source):
    """Project the drawn endpoint back to its boundary port along its tangent.

    Filled markers use a 5px source gap and an 11px destination path gap
    (6px tip extension plus 5px visual clearance). Endpoints must be outside
    their node, and the projected port must still meet the declared node.
    """
    point = points[0] if source else points[-1]
    neighbors = points[1:] if source else reversed(points[:-1])
    neighbor = next((p for p in neighbors if math.dist(point, p) > EPS), None)
    if neighbor is None:
        return False
    x, y = point
    left, top, width, height = bounds
    if left <= x <= left + width and top <= y <= top + height:
        return False
    dx, dy = x - neighbor[0], y - neighbor[1]
    if abs(dy) <= EPS:
        if not ((x < left and dx > 0) or (x > left + width and dx < 0)):
            return False
    elif abs(dx) <= EPS:
        if not ((y < top and dy > 0) or (y > top + height and dy < 0)):
            return False
    else:
        return False  # Boundary ports are perpendicular to their node edge.
    length = math.hypot(dx, dy)
    gap = 5.0 if source else 11.0
    port = (x + gap * dx / length, y + gap * dy / length)
    return on_perimeter(port, bounds)


def canonical_end_marker(node, markers):
    """The endpoint offset assumes one canonical 6px-extending end marker."""
    reference = re.fullmatch(r"url\\(\\s*(['\\\"]?)#([^'\\\"\\s)]+)\\1\\s*\\)", node.attrs.get("marker-end", ""))
    if reference is None:
        return False
    matches = markers.get(reference.group(2), [])
    if len(matches) != 1:
        return False
    marker = matches[0]
    if marker.attrs.get("markerunits") != "userSpaceOnUse" or marker.attrs.get("orient") != "auto":
        return False
    try:
        if any(number(marker.attrs.get(key, "")) != value for key, value in
               {"markerwidth": 8, "markerheight": 8, "refx": 2, "refy": 4}.items()):
            return False
        if "viewbox" in marker.attrs and numbers(marker.attrs["viewbox"].replace(",", " "), 4) != (0, 0, 8, 8):
            return False
        shapes = [child for child in marker.children if child.tag not in {"title", "desc"}]
        if len(shapes) != 1 or shapes[0].tag != "path":
            return False
        path = shapes[0].attrs.get("d", "").strip()
        return path.endswith(("z", "Z")) and path_points(path[:-1]) == [(0, 0), (8, 4), (0, 8), (2, 4)]
    except ValueError:
        return False


'''
    text = text.replace('def selector_may_match(', helper + 'def selector_may_match(')
    text = text.replace('not on_perimeter(obj.points[0 if index == 0 else -1], endpoint.bounds)',
                        'not endpoint_meets_port(obj.points, endpoint.bounds, index == 0)')
    text = text.replace('r"offset(?:-', 'r"marker(?:-(?:start|mid|end))?|offset(?:-')
    text = text.replace('    for node in protected:\n', '''    for node in protected:
        if any(node.attrs.get(key, "none") != "none" for key in ("marker-start", "marker-mid")):
            fail(node, "architecture delta permits only an end marker")
        if "marker-end" in node.attrs and node.attrs.get("data-kind") != "relationship":
            fail(node, "marker-end must be explicit on a relationship path")
''')
    text = text.replace('    objects = []\n', '''    markers = {}
    for node in scanner.nodes:
        if node.tag == "marker" and within(node, root):
            markers.setdefault(node.attrs.get("id", ""), []).append(node)
    objects = []
''')
    text = text.replace('        elif kind == "relationship":\n', '''        elif kind == "relationship":
            if not canonical_end_marker(node, markers):
                fail(node, "relationship requires a defined canonical filled marker-end (8x8, refX=2, refY=4, userSpaceOnUse)")
''')
    return text.replace('drawn relationship endpoint does not meet component',
                        'relationship clearance/tangent does not resolve to component')


def main():
    # Runtime references: retain all 45 type grammars and non-style workflows.
    extra = ['semantic-patterns.md', 'layout-budget.md', 'primitives-core.md',
             'primitive-annotation.md', 'primitive-icons.md',
             'output-spec.md', 'import-drawio.md', 'import-mermaid.md',
             'import-excalidraw.md']
    for path in sorted((BASE / 'references').glob('type-*.md')) + [BASE / 'references' / n for n in extra]:
        text = adapt_reference(path)
        if path.name == 'primitives-core.md':
            text = replace_sections(text, lambda h: h in {'Background', 'Arrow markers (define all three, always)'},
                '## Visual primitives\n\nUse the white background and marker definitions in [visual-style.md](visual-style.md).\n\n')
            duplicate = '## Visual primitives\n\nUse the white background and marker definitions in [visual-style.md](visual-style.md).\n\n'
            text = text.replace(duplicate + duplicate, duplicate)
            text = text.replace('the commented dotted-paper pattern, and ', '')
            text = text.replace("The copied template already carries the background rect, all three arrow markers, so load this file when you need exact markup or a rule's edge cases.", 'The SVG template provides a white background and one default filled marker. Add required marker variants from visual-style.md. Load this file for primitive markup and connector edge cases.')
            text = re.sub(r'\*\*Font substitution\.\*\*.*?(?=\n\n)', '**Font substitution.** Estimate full-width CJK glyphs at about 1em, then check actual text bounds in the renderer. System font fallback affects width. Measure each label and keep padding; the geometry verifier checks masks against nodes but cannot prove that text fits.', text, flags=re.S)
            text = text.replace('≤14 characters, all-caps, centered on segment midpoint.', 'Short labels centered on the segment midpoint; size the mask for the actual glyphs.')
            text = text.replace('(sublabel role, mono)', '(sublabel role)')
        if path.name == 'type-it-state.md':
            text = text.replace('### 3.3 Markers MUST touch the destination rectangle', '### 3.3 Marker clearance at the destination')
            text = re.sub(r"The path's last command ends.*?(?=\n\n)", 'Route to the correct destination edge, never its centroid. Geometry formulas identify boundary ports. Apply the filled-marker clearance from visual-style.md to the final path: start 5px outside the source and end 11px before the destination along the final direction. The arrow tip then has 5px clearance.', text, flags=re.S)
            text = re.sub(r'  - \*\*All three Survey-side.*?(?=\n)', '  - **All three Survey-side → Shared Drive connectors (C1 / C2 / C3) enter the LEFT edge.** Fan their boundary ports at y = 108 / 124 / 140, then apply the marker clearance along the right-going paths.', text)
            text = re.sub(r'\*\*Marker-visibility rule of thumb:\*\*.*?Translation:', '**Marker visibility:** keep the entire marker outside the target. The filled marker extends 6px beyond the path endpoint; leave 11px between that endpoint and the target to obtain 5px tip clearance. Choose the entry side by final travel direction:', text, flags=re.S)
            text = text.replace('marker triangle visibly touches the destination rectangle edge', 'marker tip remains 5px clear of the destination rectangle edge')
            text = text.replace('**Marker not touching the target.** Path ends at the centroid or stops short of the border.', '**Incorrect marker clearance.** Path ends at the centroid, overlaps the target, or leaves an unexplained gap. Use a 5px source gap and an 11px target path gap for the filled marker.')
        if path.name == 'output-spec.md':
            text = re.sub(r'### Visual values.*?(?=### Safe areas)', '', text, flags=re.S)
            text = text.replace('## Type Visual values', '### Type sizes')
            text = re.sub(r'`min-width` that disagrees.*?type ramp with it\.\n', '', text, flags=re.S)
            text = replace_sections(text, lambda h: h == '1. Format', '')
            text = replace_sections(text, lambda h: h == 'Holding the canvas on a narrow screen',
                '### Display dimensions\n\nSet the SVG width and height consistently with its viewBox and intended display size. Keep text readable at that size. If a figure is too dense, split it or use an overview plus detail; do not reduce text size to fit.\n\n')
            text = text[text.index('## 2. Size'):]
            text = '# SVG output spec — size, detail, audience\n\nSet these three decisions before drawing. Defaults: `doc-inline`, `balanced`, and `mixed`. The deliverable is always a self-contained SVG. Infer choices from the request and clarify only material ambiguity.\n\n' + text
            rows = text.splitlines()
            sizing = False
            for i, row in enumerate(rows):
                if row.startswith('| Preset |'):
                    sizing = True
                if sizing and row.startswith('|'):
                    cells = [c.strip() for c in row.strip('|').split('|')]
                    rows[i] = '| ' + ' | '.join(c for j, c in enumerate(cells) if j != 3) + ' |'
                elif sizing:
                    sizing = False
            text = '\n'.join(rows)
            text = re.sub(r'^.*Requested non-HTML formats.*$', '- [ ] Standalone SVG passes XML, accessibility and structural checks?', text, flags=re.M)
            text = text.replace('`balanced` and `simplified` sit inside the standard complexity budget (SKILL.md §7).',
                'These detail ceilings are upper bounds. For `balanced` and `simplified`, also apply the chosen type and SKILL.md §7 budgets, using the strictest limit (normally 9 nodes and 12 edges). Split when either limit is exceeded.')
        if path.name == 'type-architecture-delta.md':
            text = text.replace("The path's start meets the source rectangle's perimeter and its end meets the target's perimeter, within 2px for stroke/arrow-cap rounding.",
                "Use the filled marker from visual-style.md. Start 5px outside the source boundary port and end 11px before the target boundary port along the path tangent. The arrow tip then clears the target by 5px. The verifier projects each endpoint along its tangent back to its declared component perimeter, with 2px tolerance for rounding; a nearby but misdirected endpoint does not pass.")
            text += '\nDeclare `marker-end` explicitly on every relationship path and point it to the canonical filled marker in visual-style.md. Only an end marker is supported: omit `marker-start` and `marker-mid`. Marker placement through CSS or ancestor attributes is unsupported because the endpoint offsets assume this exact marker geometry.\n'
        if path.name == 'type-quadrant.md':
            text = re.sub(r'same house skin \([^)]*\)', 'the same visual palette', text)
            text = re.sub(r'^- Sans-serif H1.*\n', '', text, flags=re.M)
            text = re.sub(r'^Everything else — paper.*$', 'Use the shared visual palette, legend strip, 4px grid and complexity budget.', text, flags=re.M)
            text = re.sub(r'^- \*\*Paper / bg / pattern\*\*:.*$', '- **Background**: white, with no pattern.', text, flags=re.M)
            text = re.sub(r'^- Plain white background.*\n', '', text, flags=re.M)
        if path.name == 'type-treemap.md':
            text = text.replace('Opaque paper mask prevents the dot pattern showing through the tint', 'Opaque white mask keeps the tint independent of content behind it')
            text = re.sub(r' `ink` is a role, not a colour:.*?(?=\n)', '', text)
            text = re.sub(r'^- \*\*Contrast:\*\*.*$', '- **Contrast:** measure text against the actual composited cell fill. Keep ordinary text at least 4.5:1; use primary ink when secondary text does not pass. Preserve the area encoding and distinguish the focal cell with an outline as well as color.', text, flags=re.M)
            text = text.replace('(`0.16 → 0.10 → 0.05` on light paper, `0.14 → 0.09 → 0.04` on dark)', '(`0.16 → 0.10 → 0.05`)')
        if path.name == 'type-bar.md':
            text = re.sub(r'\*\*Non-text contrast:.*?(?=\n\n)', '**Non-text contrast:** measure dot outlines and connectors against the actual background; they must reach 3:1. Preserve hollow/solid endpoints in addition to color so the two states remain distinguishable in greyscale. Use the semantic palette and a contrasting outline instead of relying on tint alone.', text, flags=re.S)
            text += '\n## Dumbbell rule verification\n\nRun `python3 <skill-dir>/scripts/verify-dumbbell.py` with no positional file argument. It checks the documented domain formula and palette contrast constants; it does not inspect an authored SVG. Check the actual SVG with check_svg.py and inspect its values, geometry and rendered contrast separately.\n'
        if path.name == 'semantic-patterns.md':
            text = text.replace('**Nearest visual type:** **Tree**', '**Validation:** Run `python3 <skill-dir>/scripts/verify-block-registry.py <file.svg>` for this pattern. It checks nonempty unique block IDs, names, resolvable parent IDs and absence of parent cycles within each SVG. Keep referenced parents represented in that file, including context nodes when a hierarchy is split.\n\n**Nearest visual type:** **Tree**')
        if path.name == 'type-exploded.md':
            text = text.replace(' Animated parts add `data-closed-z`.', '')
            text = text.replace('<g data-exploded ', '<g data-exploded="" ')
            text = text.replace('it stays correct throughout an explode', 'it remains correct in the static exploded view')
            text = text.replace('Nothing is clipped at the closed frame either, because the closed object fits inside the exploded one.', 'The assembled geometry also fits inside these bounds.')
        if path.name == 'type-axonometric-plan.md':
            for flag in ['data-axo-plan', 'data-plate', 'data-box', 'data-room']:
                text = re.sub(r'\b' + flag + r'(?=[ >])(?!\s*=)', flag + '=""', text)
            text = text.replace('data-room="" data-name data-rect>', 'data-room="" data-name="NAME" data-rect="x0 y0 x1 y1 r">')
            text = text.replace('data-role="tag" data-name data-at=', 'data-role="tag" data-name="NAME" data-at=')
        if path.name == 'type-polar.md':
            text = text.replace('The only external stylesheet allowed is Google Fonts.', 'External stylesheets and font downloads are forbidden. Declare the CJK system font stack with a `font-family` presentation attribute on the root SVG or text elements; this grammar does not permit a style element inside the chart.')
            text += '\n## Verification\n\nRun `python3 <skill-dir>/scripts/verify-polar.py <file.svg>` to check the declared data, radial encoding, SVG allowlist and label bindings. Use check_svg.py as well for the common SVG contract.\n'
        if path.name == 'type-line.md':
            text = re.sub(r'Check the token you actually ship:.*?(?=\n)', 'Measure the actual stroke/background contrast; weight remains a redundant cue in greyscale.', text)
            text = re.sub(r'- \*\*Legend wording.*?(?=\n)', '- **Legend wording:** name the encoded quantity and its ordering; do not rely on color alone.', text)
            text = text.replace('which is false on one of the two skins', 'without a quantitative legend')
        if path.name == 'type-loop.md':
            text = text.replace('The one dark element: `ink` fill, `paper` text', 'A data/output surface from the semantic palette')
            text = text.replace('the hub alone uses the dark `ink` fill', 'the hub uses a distinct data/output surface')
            text = re.sub(r'With the canonical marker .*?`marker_overhang = 1.2`:', 'With the filled marker in visual-style.md, use `marker_overhang = 11` (6px tip extension plus 5px clearance):', text)
            text = text.replace('The arrowhead overhang completes the final 1.2px to `q_entry(j)`, landing on the box edge without crossing its stroke.', 'The arrowhead extends 6px past the endpoint, leaving 5px of clearance before the target edge.')
            text = text.replace('marker_gap = 6                         # 4..8px; 6px canonical', 'marker_gap = 11                        # 6px arrowhead + 5px clearance')
            text = text.replace("connectors begin at the circle's clockwise exit from the source box and end just before its counterclockwise entry into the destination box, so the marker tip lands on the destination stroke.",
                'connectors begin 5px beyond the clockwise exit from the source box and end before the counterclockwise entry into the destination box, leaving visible marker clearance.')
            text = text.replace('phi_entry = atan2(', 'phi_exit  = atan2(q_exit(k).y - cy, q_exit(k).x - cx)\nphi_start = phi_exit + 5 / R\nq_start   = C + R * (cos(phi_start), sin(phi_start))\nphi_entry = atan2(')
            text = text.replace('M q_exit(k).x q_exit(k).y', 'M q_start.x q_start.y')
            text = text.replace('leaving 5px of clearance before the target edge.', 'leaving approximately 5px of clearance before the target edge. These arc-length offsets are a first estimate: inspect the marker tangent against the actual rectangle edge and increase the offset when needed to maintain at least 5px clearance.')
            text = text.replace('spoke_start(k) = P_k - d_station * u_k', 'spoke_start(k) = P_k - (d_station + 5) * u_k')
            text = text.replace('paper or optional dot grid', 'white background')
            text = text.replace('| Spoke label | `arrow-label` role, `soft`,', '| Spoke label | `arrow-label` role, `muted`,')
            text = text.replace('The nodes mask microscopic connector overshoot, while every intended endpoint still lands on an edge.', 'Keep paths and marker tips outside the nodes with the specified clearance.')
            text = text.replace('destination markers land on station edges', 'destination marker tips clear station edges by at least 5px')
            text = text.replace('Every ring marker lands on a station edge, not its center.', 'Every ring marker points toward the destination boundary and clears it by at least 5px.')
            text = text.replace("Every dashed spoke begins on a station's inner edge", "Every dashed spoke begins 5px beyond a station's inner edge")
        if path.name == 'type-radar.md':
            text = text.replace('Light and dark values for every slot live in', 'Values for every slot live in')
            for old, new in [('sage','green'), ('dusty-blue','blue'), ('mustard','orange'), ('rust-brown','pink'), ('slate','purple')]:
                text = text.replace('| ' + old + ' |', '| ' + new + ' |')
        if path.name == 'type-medallion.md':
            a = text.index('**Field-value wrapping rule:**')
            b = text.index('\n\n', text.index('The HTML namespace', a))
            text = text[:a] + '''**Field-value wrapping rule:** use native SVG `<text>` and one `<tspan>` per measured line. Keep the full field value; when it exceeds 140px, split at word or CJK boundaries into at most two lines. Use 10px secondary text with a 13px line step, and expand the field row and following baselines if necessary. Never embed an HTML element or foreignObject.

```xml
<text x="field_x" y="field_y" fill="{muted}" font-size="{secondary-size}">
  <tspan x="field_x" dy="0">First line</tspan>
  <tspan x="field_x" dy="13">Second line</tspan>
</text>
```''' + text[b:]
            text = text.replace('(foreignObject, height 24)', '(text/tspan, measured two-line height)')
        if path.name == 'primitive-icons.md':
            text = icon_guidance()
        if path.name == 'type-heatmap.md':
            text = text.replace('Flip text color to paper when fill opacity ≥ 0.40 (the ink ramp becomes dark enough to carry white); keep ink text below that threshold.', 'Choose `ink` or `paper` text by measuring the actual composited fill; use whichever reaches 4.5:1. Do not use a fixed opacity threshold to infer contrast.')
        if path.name == 'import-drawio.md':
            # The source color is input data, not an output token.
            text = text.replace('`#f8cecc` / `#ec4899`', '`#f8cecc` / `#b85450`')
        write('references/' + path.name, svg_scope(finish_guidance(text)))
    old = OUT / 'references/diagram-types.md'
    if old.exists():
        old.unlink()

    main_text = (BASE / 'SKILL.md').read_text()
    main_text = re.sub(r'6\. Decorative-only SVG[^\n]*', '6. Decorative-only SVG carries `aria-hidden="true"` instead.', main_text)
    main_text = replace_sections(main_text, lambda h: h.startswith(('0.', '5.', '8.', '10.')), lambda h: {
        '0.': '',
        '5.': '## 5. Visual system\n\nRead [visual-style.md](references/visual-style.md) before drawing. It owns all colors, fonts, text sizes, node surfaces and marker appearance. Type references own geometry, relation semantics and budgets. Resolve every visual placeholder through this file.\n\n',
        '8.': '## 8. Context\n\nUse supplied prose and project materials as evidence for the SVG. Keep the figure focused on the relationship the reader needs; do not duplicate whole explanatory paragraphs inside it. The deliverable is the SVG figure.\n\n',
        '10.': '## 10. SVG template\n\nStart with [template.svg](assets/template.svg). Write valid, self-contained SVG directly. Keep visible labels and all semantic relationships in one complete static figure.\n\n',
    }[h[:2] if h.startswith(('0.', '5.', '8.')) else '10.'])
    main_text = replace_sections(main_text, lambda h: h == 'Typography:', '')
    a = main_text.index('**Typography:**')
    b = main_text.index('## 10.', a)
    main_text = main_text[:a] + '**Visual check:**\n\n- [ ] Palette, CJK system fonts, text sizes and arrow appearance match [visual-style.md](references/visual-style.md)?\n- [ ] Actual rendering is legible, with no clipping or collisions?\n\n' + main_text[b:]
    main_text = re.sub(r'^.*(?:wiretext|JetBrains|Dark mode \+|Shadow on|rounded-2xl|Hand-drawn variant|Terminal / CLI-window|Sketchy variant|assets/icons\.html).*(?:\n|$)', '', main_text, flags=re.M)
    main_text = re.sub(r' The static templates .*?(?=\n)', '', main_text)
    main_text = main_text.replace('background, dotted paper, markers', 'background, markers')
    main_text = main_text.replace('and a Geist Mono sublabel', 'and a secondary sublabel')
    main_text = main_text.replace('6. Decorative-only SVG, such as the glyphs in `assets/icons.html`, carries `aria-hidden="true"` instead.', '6. Decorative-only SVG carries `aria-hidden="true"` instead.')
    main_text = re.sub(r'^.*\[primitive-sketchy.*\n', '', main_text, flags=re.M)
    main_text = main_text.replace('style guide', 'visual specification')
    main_text = main_text.replace('editorial design system', 'light visual system with CJK system fonts')
    main_text = main_text.replace('no external except Google Fonts', 'no external fonts or assets')
    main_text = re.sub(r'\(From a repository checkout, run `[^`]+`\.\)', '(Verify label geometry in the rendered result.)', main_text)
    main_text = re.sub(r'From a repository checkout, also run .*?; from an installed skill, ', 'From the installed skill, ', main_text)
    main_text = common(main_text)
    main_text = re.sub(r'version: "[^"]+"', 'version: "0.1.1"', main_text)
    main_text = replace_sections(main_text, lambda h: h == '12. Output', '''## 12. Output

Deliver a self-contained `.svg` file directly at the requested destination. Use inline SVG shapes, local CSS and CJK system fonts. Do not create an HTML wrapper, raster output, JavaScript controller or external asset dependency. Preserve the complete meaning in the static SVG.

Follow the six-point [accessible SVG contract](references/primitives-core.md#accessible-svg-contract): role and naming attributes, title first, diagram-prefixed unique IDs, a short title, a content description, and hidden decorative-only symbols.

Run `python3 <skill-dir>/scripts/check_svg.py <file.svg>`. Follow the chosen type and semantic pattern references for additional checks, using their documented arguments; some checks validate rule constants and do not accept an SVG path. Where no extra command is provided, use the reference's checklist. Inspect the rendered figure at the intended display width; automated checks cannot establish text fit, contrast, or factual correctness. Report material simplifications from an import alongside the file.
''')
    write('SKILL.md', svg_scope(finish_guidance(main_text)))

    # Importers extract source semantics; the only image output is SVG.
    for name in ['drawio_extract.py', 'mermaid_extract.py', 'excalidraw_extract.py']:
        text = (BASE / 'scripts' / name).read_text().replace('diagram-design', 'document-diagrams')
        write('scripts/' + name, text)

    # Only diagram validators referenced by installed guidance are needed.
    validators = set()
    for path in (OUT / 'references').glob('*.md'):
        validators.update(re.findall(r'scripts/(verify-[\w-]+\.py)', path.read_text()))
    validators.update({'verify-geometry.py', 'verify-block-registry.py'})
    for name in sorted(validators):
        source = ROOT / 'upstream/diagram-design/scripts' / name
        text = source.read_text()
        text = text.replace('ROOT / "skills/diagram-design/assets"', 'ROOT / "assets"')
        text = text.replace('ROOT / "skills" / "diagram-design" / "assets"', 'ROOT / "assets"')
        text = text.replace('ROOT / "skills/diagram-design/references', 'ROOT / "references')
        text = text.replace('diagram-design', 'document-diagrams')
        for old, new in COLORS.items():
            text = text.replace(old, new)
        text = text.replace('"#3b82f6", "#f08a59"', '"#3b82f6"')
        text = text.replace('light and dark skin accent tokens', 'focal accent token')
        text = text.replace('rgba(79,93,117,0.15)', 'rgba(100,116,139,0.15)')
        text = text.replace(r'rgba\(\s*191\s*,\s*69\s*,\s*32\b', r'rgba\(\s*59\s*,\s*130\s*,\s*246\b')
        text = text.replace('the shipped Geist / Geist Mono faces', 'reference Latin faces (only an estimate for system-font fallback)')
        text = re.sub(r'skills/document-diagrams/assets/example-[\w-]+\.html', 'path/to/diagram.html', text)
        text = text.replace('.html', '.svg').replace('HTML files', 'SVG files').replace('HTML file', 'SVG file')
        text = text.replace('HTML diagrams', 'SVG diagrams')
        text = text.replace('Architecture delta HTML contract', 'Architecture delta SVG contract')
        text = text.replace('Architecture containment HTML contract', 'Architecture containment SVG contract')
        if name == 'verify-geometry.py':
            text = text.replace('Shape heuristics follow the shipped templates:', 'Shape heuristics follow the SVG primitives:')
            text = text.replace('labels and zone eyebrows. The width cap covers the long mono plates shipped\n  in example-sequence-oauth.svg (128px) and the wider plates CJK labels need\n  at the same glyph count.', 'labels and zone eyebrows. The width cap covers long label plates (128px)\n  and the wider plates CJK labels need at the same glyph count.')
        text = text.replace('see export-registry.md "What this never does"', 'the embedded metadata is independent of visible layout')
        if name == 'verify-dumbbell.py':
            a = text.index('2. NON-TEXT CONTRAST')
            b = text.index('The check FAILS CLOSED.', a)
            text = text[:a] + '2. NON-TEXT CONTRAST - connector and endpoint boundaries must reach 3:1\nagainst the white background. Shape and text retain the series identity.\n\n' + text[b:]
            text = text.replace('PAPER_LIGHT, PAPER_DARK = "#ffffff", "#1e293b"', 'PAPER_LIGHT = "#ffffff"')
            text = re.sub(r'^.*\("connector \(dark\)".*\n', '', text, flags=re.M)
            text = re.sub(r'^.*\("solid endpoint stroke \(dark\)".*\n', '', text, flags=re.M)
            text = text.replace('"rgba(45,49,66,0.55)"', '"rgba(30,41,59,0.55)"')
            text = text.replace('    "rgba(245,245,245,0.40)",\n', '')
            text = text.replace('in both themes', 'against the white background').replace('in each theme', 'on white')
        if name == 'verify-architecture-delta.py':
            text = delta_clearance(text)
        if name == 'verify-polar.py':
            text = text[:text.index('ROOT = Path(')] + text[text.index('TOLERANCE ='):]
            text = text.replace('from urllib.parse import urlsplit\n', '')
            text = re.sub(r'def _allowed_stylesheet\(href: str\) -> bool:.*?(?=\ndef _style_property)', 'def _allowed_stylesheet(href: str) -> bool:\n    return False  # Standalone SVG has no external stylesheet dependencies.\n\n', text, flags=re.S)
            text = text.replace('        paths = list(DEFAULT_PATHS)', '        print("Usage: verify-polar.py FILE.svg [FILE.svg ...]", file=sys.stderr)\n        return 2')
            text = text.replace('    def _in_chart(self)', '''    def handle_pi(self, data: str) -> None:
        if data.split(None, 1)[:1] != ["xml"]:
            self.parse_findings.append("processing instructions, including XML stylesheets, are forbidden")

    def _in_chart(self)''')
            text = text.replace('one HTML document', 'one SVG document')
        if name == 'verify-heatmap.py':
            text = text.replace('(245, 245, 245)', '(255, 255, 255)')
            text = text.replace('underlay rather than assuming the light paper background. In dark heatmaps, the\n    underlay is the dark paper color (#1e293b), not #ffffff.', 'underlay, with white as the default background.')
            text = text.replace('        rm = RGBA_RE.search(fill)', '        raw_rgb = _parse_color(fill)\n        rm = RGBA_RE.search(fill)')
            text = text.replace('                b_ch = int(rm.group(3))', '                b_ch = int(rm.group(3))\n                raw_rgb = (r_ch, g_ch, b_ch)')
        write('scripts/' + name, color_verifier(name, text))
    source = (ROOT / 'upstream/diagram-design/scripts/axonometry.py').read_text()
    # Projection and prism geometry only; skins and page builders are presentation.
    projection = '\n'.join([
        '"""2:1 dimetric projection and rounded-prism geometry for SVG."""',
        'from __future__ import annotations', 'import math', 'from dataclasses import dataclass',
        'S2 = math.sqrt(2)', source[source.index('# ---------------------------------------------------------------- projection'):source.index('FONT_LINK')],
    ])
    write('scripts/axonometry.py', projection)
    # Remove only obsolete generated resources, leaving independently maintained SVG assets intact.
    for relative in ['references/animation.md', 'references/export.md', 'references/export-registry.md',
                     'assets/template.html', 'assets/template-motion.html', 'scripts/self_check.py',
                     'scripts/export_svg.py', 'scripts/export_png.py', 'scripts/verify-motion.py']:
        (OUT / relative).unlink(missing_ok=True)
    print('Assembled 45 SVG type references, semantics, layout, importers and structural verifiers.')


if __name__ == '__main__':
    main()
