"""Replace presentation-only color rules while retaining type geometry and meaning.

Called after the existing source adaptation. Kept out of the installed skill.
"""
import re


ROLE_SURFACE = 'Use the semantic role fill/stroke/dark-text triple from visual-style.md on both ordinary and focal nodes. Keep the stated focal count and emphasize those nodes with border weight; role colors do not consume focal slots.'
SERIES = 'Use consistent semantic or categorical series colors from visual-style.md, including on non-focal series. Keep direct labels and the legend; choose a contrasting stroke or dark counterpart when needed. Focal emphasis uses the existing weight/dot treatment and keeps the series hue.'


def guidance(name, text):
    def replace(pattern, value):
        nonlocal text
        text = re.sub(pattern, value, text, flags=re.M)

    # Count claims rather than instances of a paint token, throughout all budgets.
    text = text.replace('accent elements', 'focal elements').replace('accent nodes', 'focal nodes')
    if name == 'SKILL.md':
        replace(r'^- accent is .*$', '- **Semantic color identifies a role; focal emphasis identifies the editorial point.** Apply role colors to all matching nodes. Keep 1–2 focal nodes, using border weight or the type\'s other focal cues; semantic colors do not count against that budget.')
        replace(r'^\| accent on every .*$', '| Focal emphasis on every node | Keep 1–2 focal claims; repeated semantic colors are expected |')
        replace(r'^- \[ \] accent used on .*$', '- [ ] Semantic roles consistently colored, including non-focal items? Focal count within the type budget, counted independently of hue?')
        replace(r'^- \*\*Arrows:\*\*.*$', '- **Arrows:** choose gray for neutral relationships or the semantic color for input, processing, output, analysis or danger from visual-style.md. Keep dashed `5,4` for optional, passive, return or async relations, and the type\'s specific relation styles, dash patterns, marker kinds and focal selection. Draw arrows before boxes so lines sit behind nodes.')
    # Component override caps were styling limits, not content budgets.
    replace(r'^(\d+\.) (?:Custom component colors|Custom-colored cells|≤ 3 custom-colored components).*$', r'\1 Apply semantic role colors consistently, including on non-focal components; role colors do not consume focal slots.')
    replace(r'^\| Custom-colored elements[^\n]*$', '| Semantic-colored elements | Not limited by the focal budget; use consistent role colors |')
    text = text.replace('Cap at 2 custom-colored components in addition to the focal.', 'Semantic component colors are independent of focal count.')
    text = text.replace('Optional color inputs select a semantic palette;', 'Optional color inputs select a semantic role for any component, including a focal one;')
    replace(r'^- \*\*Custom color on a focal component\.\*\*.*$', '- **Replacing a focal component\'s semantic role with an arbitrary highlight hue.** Preserve its role color and emphasize its outline.')
    replace(r'^- Custom `color: "#hex"` on a focal component.*$', '- A focal component retains its semantic role color; focus adds outline weight.')
    replace(r'^- \*\*`color` override on a focal component\*\*.*$', '- **Color that contradicts the component role.** Focal and ordinary components use the same role palette.')
    text = text.replace('Ignored on `kind: focal` (accent wins).', 'Applies to focal nodes too; emphasis changes border weight.')
    text = text.replace('`focal` triggers the accent palette (§5)', '`focal` adds editorial emphasis (§5) without replacing the semantic palette')
    text = text.replace('2 accent elements', '2 focal elements')
    text = text.replace('the design system has one accent', 'roles map to a consistent semantic palette')
    text = text.replace('One accent plus the ink ramp replaces the source theme.', 'Semantic role colors with separate focal emphasis replace the source theme.')
    text = text.replace('one accent plus the ink ramp', 'semantic role colors with separate focal emphasis')
    text = text.replace('White services, ink-tint store, one accent', 'Role-colored services and stores with separate focal emphasis')
    text = text.replace('White services, ink-tint stores, one accent', 'Role-colored services and stores with separate focal emphasis')
    replace(r'^- \*\*`color` override on a focal element\*\*.*$', '- **Discarding a focal element\'s semantic color.** Keep its role palette and add outline emphasis.')
    replace(r'^- \*\*Colors\*\*: choose `color:.*$', '- **Colors:** assign the shared semantic palette to every evidenced role. Repeated role colors do not consume focal slots.')
    replace(r'^- \*\*Lane tints over-applied\*\*.*$', '- **Unexplained lane tints.** Use quiet, consistent role/category surfaces for lanes; retain clear node boundaries and lane labels.')
    text = text.replace('the single ink ramp is the honest encoding', 'one shared-hue ramp is the honest encoding')
    text = text.replace('that no non-focal cell uses accent fill', 'that non-focal cells share a hue and a monotone opacity ramp')
    text = text.replace('an unexplained accent fill', 'an unexplained off-ramp fill or emphasis')

    rules = {
        'primitives-core.md': [
            (r'Uppercase names \(`X`, `FILL`, `STROKE`\) are geometry and per-node values you compute\.', 'Uppercase geometry names such as `X` are computed per node. Resolve `FILL`, `STROKE` and `TEXT` to its semantic fill, contrast-checked outline and dark text color.'),
            (r'fill="STROKE@0\.8"', 'fill="TEXT"'),
        ],
        'import-drawio.md': [
            (r'^\| `#dae8fc` / `#6c8ebf`.*', '| `#dae8fc` / `#6c8ebf` (blue) | generic component | Input/primary for entry points; Processing for services, according to the label |'),
            (r'^\| `#d5e8d4`.*', '| `#d5e8d4` / `#82b366` (green) | ok / primary path | Data/output/success semantic surface; focal selection is independent |'),
            (r'^\| `#ffe6cc`.*', '| `#ffe6cc` / `#d79b00` (orange) | attention / queue | Processing/in-progress surface; Warning if the label identifies a risk |'),
            (r'^\| `#f8cecc`.*', '| `#f8cecc` / `#b85450` (red) | failure / risk / legacy | Sensitive/warning surface for evidenced risk; retain state labels and actual relationship semantics |'),
            (r'^\| `#e1d5e7`.*', '| `#e1d5e7` / `#9673a6` (purple) | analysis or external / third-party | AI/analysis when supported by content; neutral external context otherwise |'),
            (r'^\| `#ffffff` / grey.*', '| `#f5f5f5` / grey | infrastructure / background | Semantic role surface for a component; quiet neutral surface for a grouping container |'),
            (r'^\| no fill \|.*', '| no fill | unstyled | Infer role from the content; use neutral context if unknown |'),
            (r'Store/State box \(`ink @ 0\.05` fill, `muted` stroke\)', 'Store/State box with the Data/output semantic surface'),
            (r'The one accent node', 'The focal node, retaining its role color'),
        ],
        'type-flowchart.md': [
            (r'^- Shape carries type, not color:', '- Shape carries control-flow type; semantic color adds role/status information:'),
            (r'^- Using fill color to signal node type.*', '- Using color alone to signal a decision or terminal. Keep the prescribed shape alongside semantic fills.'),
            (r'^- Use accent on the happy path.*', '- Emphasize the happy path or the single most consequential decision. Color all nodes by their semantic roles; repeated role colors are not additional focal decisions.'),
        ],
        'type-architecture-delta.md': [(r'^Color is secondary\..*', 'Every change remains readable from its existing text code and shape/line treatment. Use semantic role/status colors consistently, including on non-focal objects; unchanged objects remain quiet context. Focal emphasis is separate from the change codes and does not alter their meaning.')],
        'type-layers.md': [
            (r'^- Fills:.*', '- Fills: use semantic role surfaces for the layers; keep neutral fills where a layer has no evidenced role. Preserve stacking order and separators.'),
            (r'^- Every layer a different color.*', '- Arbitrary per-layer colors without stable role meanings or labels.'),
        ],
        'type-pyramid.md': [(r'^- Fill:.*', '- Fill: use consistent semantic or categorical surfaces per level; quantities remain encoded by the type\'s geometry, not arbitrary hue or saturation.')],
        'type-venn.md': [
            (r'^- Circle stroke:.*', '- Circle stroke: 1px, one consistent semantic/category color per set, with contrast checked.'),
            (r'^- Circle fill:.*', '- Circle fill: translucent semantic/category tints so overlaps remain visible. Keep set labels and name each relevant intersection; blended colors are not new quantities.'),
            (r'\*\*accent accent\*\*', '**Focal emphasis**'),
        ],
        'type-bar.md': [
            (r'^- \*\*Focal bar:\*\*.*', '- **Bar colors:** use semantic or categorical fills and matching strokes for all bars. Emphasize at most one focal bar with a heavier outline; it retains its role color.'),
            (r'^Focal bar: replace fill.*', 'Focal bar: keep its role fill and dark label color; increase the outline weight.'),
            (r'^- \*\*Stacked bars:\*\*.*', '- **Stacked bars:** segments stacked to total. Use a stable semantic/category color per segment series across bars, with one optional focal segment outlined more heavily. Document the total at the top of each stack.'),
            (r'^- Accent on more than 1 bar.*', '- Focal weight on more than one bar. Repeated semantic/category colors are allowed.'),
            (r'^- \*\*Accent marks the series, not a focal row\.\*\*.*', '- **The hollow/solid treatment identifies the paired series, not a focal row.** Repeat it on every row, with stable series hues. Do not additionally emphasize a most-changed row; the sort order already carries rank.'),
        ],
        'type-gantt.md': [(r'^- \*\*Focal task bar:\*\*.*', '- **Task colors:** use consistent phase or status colors, named in the legend. One key deliverable or critical-path task gets a heavier outline while keeping its role hue. Dates and duration geometry remain unchanged.')],
        'type-scatter.md': [
            (r'^- \*\*Point shape:\*\*.*', '- **Point shape:** `<circle>` r=5 for standard points, r=6 for focal. Use semantic/category fills with contrasting outlines; preserve the focal size cue independently of hue.'),
            (r'^- \*\*One accent bubble.*', '- **Bubble colors:** use role or category colors consistently, including on non-focal bubbles. At most one focal bubble, declared with `data-focal="true"`, receives a heavier outline without changing its data-scaled area.'),
            (r'^- \*\*The ramp runs faintest-on-largest.*', '- **Fill opacity:** use light semantic/category fills. Optional opacity compensation for large bubbles is decorative, not a numeric encoding; area alone encodes the declared third value.'),
            (r'^- \*\*Every bubble keeps a `muted` stroke\.\*\*.*', '- **Every bubble needs a contrasting outline.** Use its role/category stroke or dark counterpart at 3:1; a neutral outline is also valid. A faint fill alone is not a boundary.'),
            (r'^- A hue per item instead of the ink ramp.*', '- Arbitrary hues without semantic/category labels, or a legend that presents decorative opacity as data.'),
            (r'^- \*\*One ink fill for every non-focal dot.*', '- **One uniform non-focal fill per swarm**, chosen from a semantic palette, plus a contrasting outline; **at most one focal dot**, explicitly marked `data-focal="true"`. Density reads from swarm thickness, never from opacity. The verifier retains identical non-focal fills and the shared-radius rule.'),
            (r'^- \*\*The accent marks the editorially focal item\*\*.*', '- **Focus marks the editorially focal item**, not a category. A single-distribution swarm keeps one shared role color; separate distributions remain facets.'),
            (r'^- A hue per group instead of one ink.*', '- Mixing groups inside a single-distribution swarm without facets, or encoding density with opacity.'),
            (r'use the focal accent or facet it', 'use a labeled category color or facet it'),
        ],
        'type-sankey.md': [
            (r'^- \*\*Ribbon fill:\*\*.*', '- **Ribbon fill:** use consistent semantic/category colors for source groups or flow kinds, carried through their ribbon segments and named in the legend. Use light/translucent fills with distinguishable boundaries. The one editorial focal path may span several segments and still counts as one focus; strengthen its outline while preserving its hue. Ribbon width alone encodes quantity.'),
            (r'^- \*\*Per-flow rainbow coloring\.\*\*.*', '- **Unexplained ribbon colors.** Map hues to stable source groups or flow meanings, not unrelated decoration on each segment.'),
        ],
        'type-treemap.md': [
            (r'^- \*\*Fill:\*\*.*', '- **Fill:** use semantic/category light fills for the cells. Keep category colors stable and label every category. Area carries the share; an optional tonal ramp must not replace area or introduce a second quantity. Emphasize at most one focal cell with its heavier outline.'),
            (r'^- \*\*Stroke:\*\*.*', '- **Stroke:** 1px contrasting role/category outline on each cell; the focal cell retains its hue with a 1.5px outline.'),
            (r'^- Rainbow fills:.*', '- Unlabeled or inconsistent category hues; changing cell area to accommodate color.'),
            (r'^The treemap\'s colour section holds.*', 'Use one semantic/category color per series, repeated across every column and keyed in the legend. One optional focal segment keeps its series hue and uses the 1.5px outline plus `data-focal="true"`. Preserve column-width, conditional-height and joint-area encodings; labels use primary or semantic dark text.'),
            (r'^- One hue per series instead of the ink ramp.*', '- Inconsistent hues for the same series across columns, or a legend that gives decorative tone a numeric meaning.'),
        ],
        'type-line.md': [
            (r'^- \*\*Multi-series:\*\*.*', '- **Multi-series:** up to 5 series. ' + SERIES),
            (r'^- \*\*One accent, and an `ink` opacity ramp.*', '- **Series colors:** ' + SERIES),
            (r'^- \*\*The ramp runs 0\.80.*', '- **Line contrast:** check each actual stroke against the background at 3:1; use its semantic dark counterpart when necessary. Opacity does not encode rank or value.'),
            (r'^- \*\*Note what the ramp does not buy you.*', '- **Redundant identity:** keep endpoint labels and the legend so crossings can be followed without color.'),
            (r'^The slopegraph\'s colour section holds.*', 'Use the same series-color rules as the slopegraph, with a light tint of each series hue under its ridge. Focal stroke weight stays 2.4px against 1.2px. Mark the focal ridge path `data-focal="true"`; keep all baseline, bin and amplitude formulas unchanged. Labels use primary or semantic dark text.'),
            (r'^- \*\*One accent layer.*', '- **Layer colors:** use stable semantic/category colors keyed by series in the legend. One optional focal layer retains its hue and gains an outline. Thickness and the shared baseline retain all quantitative meaning.'),
            (r'^- Fills may run lighter than a line could:.*', '- Keep adjacent fills distinguishable with contrast-checked boundaries; no text sits on the quantitative layers. Decorative fill opacity is not a value scale.'),
            (r'^Everything the slopegraph\'s colour section says.*', 'Use the slopegraph\'s semantic/category series colors. Keep focal weight 2.4px versus 1.2px and the existing dot-size distinction. Declare `data-focal="true"` on the focal bump path, keep its series hue, and retain rank positions, ordering, labels and the shared snapshots. Focus marks the story, not automatically the winner.'),
            (r'^- One hue per (?:series|ridge|layer) instead of the ink ramp.*', '- Inconsistent or unlabeled series colors, or using decorative tone as a numerical scale.'),
        ],
        'type-heatmap.md': [
            (r'\*\*One ink ramp, one accent\.\*\*', '**One shared-hue ramp, at most one focal cell.**'),
            (r'`rgba\(INK, opacity\)`', '`rgba(ROLE_RGB, opacity)`'),
            (r'^\*\*One focal cell only\.\*\*.*', '**One focal cell only.** Declare `data-focal="true"` on the editorially focal cell; keep its role hue and strengthen its outline. It may use the documented off-ramp highlight, but must retain its value label. Blue alone is not focal. The verifier counts explicit focal metadata and checks the non-focal ramp independently of hue.'),
            (r'the ink ramp is not a gradient legend', 'the shared-hue ramp is not a gradient legend'),
        ],
        'type-waterfall.md': [
            (r'^- \*\*Sign is encoded by fill weight, not hue\.\*\*.*', '- **Sign retains its fill-weight encoding.** Increases use one consistent semantic light fill and contrasting outline; decreases are hollow (paper fill) with a contrasting role outline. Hue may reinforce meaning but never replaces tint versus hollow, bridge geometry or signed printed values.'),
            (r'^- \*\*Focal bridge \(≤1, optional\):\*\*.*', '- **Focal bridge (≤1, optional):** declare `data-focal="true"` on the contribution being discussed. Use its role hue and a heavier outline, with dark readable text. As before, this focal treatment may replace its sign fill; the signed label and geometry still carry direction.'),
            (r'fill="\{muted @ 0\.15\}" stroke="\{muted\}"', 'fill="{role-fill}" stroke="{role-stroke}"'),
        ],
        'type-fishbone.md': [(r'^- \*\*Focal rule\.\*\*.*', '- **Focal rule.** Exactly one confirmed root-cause bone and the effect box form the two focal elements. Emphasize their outlines. Other category tags and bones may use consistent semantic/category colors; keep their labels and the existing cause/effect geometry.')],
        'type-kanban.md': [
            (r'^\| `default`.*', '| `default` | Processing fill | Processing stroke | — |'),
            (r'^\| `blocked`.*', '| `blocked` | Sensitive/warning fill | Warning stroke dashed `4,4` | 4px warning bar on the card\'s left edge |'),
            (r'^\| `waiting / external`.*', '| `waiting / external` | Neutral or role fill | Role/neutral stroke dashed `4,3` | — |'),
            (r'^\| `done`.*', '| `done` | Data/output fill | Data/output stroke | — |'),
            (r'^When a column\'s card count.*', 'When a column\'s card count `n` exceeds its stated `limit`, use the warning stroke and dark warning text on its WIP chip. Apply warning styling to every over-limit chip and blocked card. These are state encodings; separately choose at most two editorial focal elements and emphasize their outlines.'),
            (r'^- Max 2 focal elements.*', '- Max 2 editorial focal elements; repeated state colors do not consume this budget.'),
            (r'^- \*\*Accenting every blocked card\.\*\*.*', '- **Giving every blocked card focal weight.** All blocked cards need the warning treatment; only the selected focal cards receive extra emphasis.'),
        ],
        'type-service-blueprint.md': [
            (r'^- \*\*Fills:\*\*.*', '- **Fills:** use semantic role surfaces within each lane. Keep lane headings and the visibility line as the explicit frontstage/backstage distinction; quiet background bands may support it.'),
            (r'^- \*\*Focal cell \(≤1, optional\):\*\*.*', '- **Focal cell (≤1, optional):** the failure, wait or handoff the figure exists to show. Retain its semantic fill and dark text, strengthen its outline, and declare `data-focal="true"`.'),
            (r'^- \*\*Accent on every failing cell\.\*\*.*', '- **Focal weight on every failing cell.** Every failure retains warning color and a label; only one receives editorial emphasis.'),
        ],
        'type-polar.md': [(r'^- One accent category maximum\..*', '- One focal category maximum. Use a consistent semantic/category palette on value rays; keep the existing focal width and radius cues and `data-polar-focal` metadata.')],
        'type-radar.md': [
            (r'One accent\. Position is the signal — color reserved for the recommended option\.', 'Color identifies series; weight and vertex dots identify the focal option.'),
            (r'^The skill\'s "1-focal" rule still holds:.*', 'Keep one focal series, using the existing heavier stroke and vertex dots. ' + SERIES),
            (r'^\| Focal \|.*', '| Focal | Its semantic/category color | Same hue, heavier stroke and vertex dots |'),
        ],
        'type-dependency.md': [
            (r'^  - Internal package/service →.*', '  - Internal package/service → semantic role surface.'),
            (r'^  - Leaf with no outgoing edges →.*', '  - Leaf with no outgoing edges → retain its semantic role surface; terminal position carries its structural role.'),
            (r'Nothing else in a dependency graph is accent\.', 'Other nodes and edges may use semantic colors without becoming focal.'),
            (r'no accent stroke or fill on the nodes themselves, or the 2-accent budget is blown on the wrong elements\.', 'semantic node colors remain valid; do not add another editorial focal treatment.'),
        ],
        'type-db-schema.md': [(r'Nothing else on the diagram is `accent`\.', 'Other tables may use semantic role colors; destructive semantics also remain explicit in the FK label and relation notation.')],
        'type-quadrant.md': [(r'^- \*\*Non-focal cells\*\*:.*', '- **Non-focal cells**: semantic/category surfaces appropriate to their content; preserve cell position and labels.')],
        'type-high-level.md': [
            (r'^\*\*Focal node:\*\*.*', '**Node surfaces:** ' + ROLE_SURFACE + ' Keep focal stroke-width 1.2 and ordinary stroke-width 1.'),
            (r'Don\'t try to "fix" this — overrides should be rare \(≤ 2 per diagram\)\.', 'Keep role colors consistent; color repetition does not add a focal claim.'),
        ],
        'type-dp-integration.md': [
            (r'Non-focal bars use `bar_h_default=44` with muted styling \(fill `ink @ 0\.05`, stroke `ink @ 0\.32`\)\.', 'Non-focal bars use `bar_h_default=44` with their semantic role fill/stroke.'),
            (r'Same fill / stroke pattern: fill `muted @ 0\.06`, stroke `soft`, stroke-width 1\.', 'Use the semantic role fill/stroke/text triple, stroke-width 1.'),
            (r'^- \*\*Per-tool color coding\*\*.*', '- **Arbitrary per-tool colors.** Assign stable semantic roles instead; every matching component may use its role color, including non-focal nodes.'),
        ],
        'type-it-state.md': [(r'^- \*\*Using `kind: focal` to flag every painful thing\.\*\*.*', '- **Using `kind: focal` for every issue.** Keep ≤2 editorial pain points; repeat the warning role on all evidenced risks without making them focal.')],
        'type-dp-security-matrix.md': [
            (r'^\| `full` \|.*', '| `full` | Input/primary fill | Input/primary stroke | Input/primary dark text | 600 |'),
            (r'^\| `rw` \|.*', '| `rw` | Processing fill | Processing stroke | Processing dark text | 400 |'),
            (r'^\| `read` \|.*', '| `read` | Data/output fill | Data/output stroke | Data/output dark text | 400 |'),
            (r'^\| `none` \|.*', '| `none` | `paper` | `rule` | `muted` | 400 |'),
            (r'^\| \*\*focal\*\* \|.*', '| **focal** | Retain level fill | Retain level stroke (1.4) | Dark level text | 600 |'),
            (r'The focal cell can carry a 2nd line.*', 'The focal cell can carry a 2nd line (`sub:`), rendered in dark semantic text at 10px. The level label remains explicit; color is redundant permission information.'),
            (r'Fill and text-color depend on `level` \(or focal flag\)', 'Fill and text-color depend on `level`; focus changes outline weight'),
        ],
        'import-excalidraw.md': [
            (r'one accent plus the ink ramp', 'consistent semantic colors, with focal emphasis chosen separately'),
            (r'White services, ink-tint store, one accent', 'Role-colored services and stores, with separate focal emphasis'),
            (r'the design system has one accent', 'map evidenced roles to the semantic palette'),
        ],
        'type-medallion.md': [
            (r'^- If `promotions\[k\]\.to` references a tier with a \*\*`color` override\*\*.*', '- Choose promotion colors by relationship meaning (processing, output or neutral), with a matching marker. Width stays at 1.4 unless focal; lifecycle arrows keep their dash. A tier\'s component color does not automatically recolor its edges.'),
            (r'^- Focal wins if both apply.*', '- A focal promotion keeps its semantic hue and uses width 1.6. The focal paint slot resolves to that hue; it does not overwrite it with blue.'),
        ],
    }
    for pattern, value in rules.get(name, []):
        replace(pattern, value)

    # Styling tables in parametric types retain all sizes, dash conventions and
    # relation-style selection. Focal is an overlay on a semantic surface.
    if name in {'type-medallion.md', 'type-process.md', 'type-data-flow.md',
                'type-it-state.md', 'type-high-level.md', 'type-dp-integration.md',
                'type-dp-security-matrix.md'}:
        text = text.replace('## 5. Focal rule', '## 5. Focal rule\n\n' + ROLE_SURFACE)
        replace(r'^\*\*Focal styling note:\*\*.*', '**Focal styling note:** retain the tier\'s semantic surface and dark role text; the 1.6px outline provides emphasis. Keep all field values legible.')
        # Replace just paint tokens in node/cell/tier treatment table rows.
        lines = text.splitlines()
        surface_table = False
        for i, line in enumerate(lines):
            if line.startswith('|') and 'Card fill' in line and 'Card stroke' in line:
                surface_table = True
            elif not line.startswith('|'):
                surface_table = False
            if surface_table and re.match(r'^\| `(?:outer|default|focal|cold|standard|normal)` \|', line):
                cells = line.split('|')
                if len(cells) >= 5:
                    cells[2] = ' `role-fill` '
                    cells[3] = re.sub(r'`(?:accent|ink|muted)(?: @ [\d.]+)?`', '`role-stroke`', cells[3])
                    for j in range(4, len(cells)-1):
                        cells[j] = re.sub(r'`(?:accent|ink|muted)(?: @ [\d.]+)?`', '`role-text`' if j > 4 else '`role-fill`', cells[j])
                    lines[i] = '|'.join(cells)
        text = '\n'.join(lines) + '\n'
        text = text.replace('accent text bold', 'dark semantic text bold')
        text = text.replace('accent fill + accent stroke', 'role fill + heavier role stroke')
        text = text.replace('accent fill + stroke', 'role fill + stroke')
        text = text.replace('Accent border + accent role chip + ink title', 'Heavier role-colored border + semantic role chip + dark role title')
        text = text.replace('Header chip and legend chip both render in accent.', 'Header and legend chips retain their semantic color with focal weight.')
        text = text.replace('Header chip and legend chip render in accent.', 'Header and legend chips retain their semantic color with focal weight.')
        text = text.replace('accent header band', 'semantic header band')
        text = text.replace('Renders bucket text and example-value lines in accent.', 'Renders bucket text and example-value lines in dark semantic text.')
        text = text.replace("The focal tier's bucket text and example values render in accent; the rest stay muted.", 'All tiers use readable dark semantic text; the focal tier retains its heavier outline.')
        text = text.replace('Focal cell stroke `accent` width 1.4.', 'Focal cell stroke `role-stroke` width 1.4.')

    # Quantitative excerpts keep geometry but no longer suggest gray as mandatory.
    if name in {'type-bar.md', 'type-gantt.md', 'type-scatter.md'}:
        text = text.replace('fill="{muted @ 0.15}" stroke="{muted}"', 'fill="{role-fill}" stroke="{role-stroke}"')
        text = text.replace('fill="{muted @ 0.20}" stroke="{muted}"', 'fill="{role-fill}" stroke="{role-stroke}"')
    if name == 'type-gantt.md':
        text = text.replace('fill="{accent @ 0.12}" stroke="{accent}" stroke-width="1"', 'fill="{role-fill}" stroke="{role-stroke}" stroke-width="1.5" data-focal="true"')
    if name == 'type-heatmap.md':
        text = text.replace('{ink @ 0.29}', '{series-color @ 0.29}')
    if name == 'type-treemap.md':
        text = text.replace('fill="{ink @ 0.16}" stroke="{ink @ 0.30}"', 'fill="{role-fill}" stroke="{role-stroke}"')
        replace(r'^Focal cell: replace the fill.*', 'Focal cell: retain its semantic/category fill and stroke hue; use a 1.5px outline and `data-focal="true"`.')
    if name == 'type-line.md':
        text = text.replace('stroke="{ink @ 0.68}"', 'stroke="{series-color}"')
        text = text.replace('fill="{ink @ 0.30}"', 'fill="{series-color @ 0.30}"')
        text = text.replace('**Fill `ink` at `0.12` on every non-focal ridge**', '**Fill each series hue at `0.12` on its non-focal ridge**')
        # Existing example focal curves are explicitly bound, independent of hue.
        text = re.sub(r'(<(?:path|polyline)\b(?=[^>]*data-(?:ridge|series)=)(?=[^>]*stroke="\{accent\}")[^>]*?)(\s*/?>)', r'\1 data-focal="true"\2', text)
    if name in {'type-scatter.md', 'type-treemap.md', 'type-waterfall.md'}:
        text = re.sub(r'(<(?:circle|rect)\b(?=[^>]*data-(?:size|value|segment|role)=)(?=[^>]*stroke="\{accent\}")[^>]*?)(\s*/?>)', r'\1 data-focal="true"\2', text)
    if name == 'type-scatter.md':
        text = text.replace('fill="{ink @ 0.55}" stroke="{muted}"', 'fill="{role-fill}" stroke="{role-text}"')
        text = text.replace('fill="{accent @ 0.55}" stroke="{accent}" stroke-width="1.2"', 'fill="{accent}" stroke="{role-text}" stroke-width="1.5"')
        replace(r'^- \*\*The focal dot keeps the shared radius\.\*\*.*', '- **The focal dot keeps the shared radius.** Use a solid role-hue fill against the ordinary light role fill, a dark 1.5px outline against the ordinary 0.75px outline, its bound label and a legend key. This is editorial emphasis, not a second quantity or a new category.')
        text = text.replace('one accent bubble', 'one explicitly declared focal bubble')
    if name == 'type-org-chart.md':
        text = text.replace('backend treatment (white + `ink`)', 'backend treatment (Processing semantic surface)')
        text = text.replace('one accent focal node', 'one focal node retaining its role color')
    if name == 'type-story-map.md':
        text = text.replace('`ink @ 0.05` fill, `muted` stroke', 'semantic/category light fill, contrasting role stroke')
        text = text.replace('Nothing else on the map is `accent`.', 'Other cards retain their semantic/category colors without additional focal emphasis.')
    if name == 'type-wardley.md':
        text = text.replace('filled `paper` with an `ink` 1px stroke', 'with a light semantic/category fill and contrasting 1px stroke, or neutral `paper`/`ink` when no role is evidenced')
    if name == 'type-high-level.md':
        text = text.replace('Stroke: `ink @ 0.20`, `stroke-width=0.8`, `rx=6`. Fill: `ink @ 0.05`.', 'Stroke: `role-stroke`, `stroke-width=0.8`, `rx=6`. Fill: `role-fill`.')
        text = text.replace('Stroke: `ink @ 0.18`, `stroke-width=0.8`, `rx=4`. Fill: `ink @ 0.05`.', 'Stroke: `role-stroke`, `stroke-width=0.8`, `rx=4`. Fill: `role-fill`.')
    if name == 'type-architecture.md':
        text = text.replace('Every box in accent ("this is important too") — hierarchy collapses.', 'Focal weight on every box — hierarchy collapses. Repeated semantic colors are valid; use a 1.5px focal outline against the ordinary 1px outline.')
    if name in {'type-line.md', 'type-scatter.md', 'type-treemap.md', 'type-waterfall.md'}:
        text = text.rstrip() + '\n\nFocal metadata: declare `data-focal="true"` on the bound focal mark itself. Semantic blue on any other mark does not make it focal; apply the existing outline/weight cues independently of hue.\n'
    return text


def verifier(name, text):
    """Separate focal identity from paint without relaxing data/geometry checks."""
    text = text.replace('accent COUNT is read here, off the stroke, as verify-beeswarm.py does.', 'focal COUNT is read here from data-focal metadata.')
    text = text.replace('this gate only pairs the accent with its stroke weight.', 'this gate pairs focal metadata with its stroke weight.')
    if name in {'verify-bubble.py', 'verify-beeswarm.py', 'verify-marimekko.py'}:
        text = text.replace('bool(ACCENT_RE.search(attrs.get("stroke", "")))', 'attrs.get("data-focal", "").lower() == "true"')
        text = re.sub(r'# The accent stroke.*?\n\)\n', '# Focal identity is declared by data-focal, independently of semantic hue.\n', text, flags=re.S)
        text = text.replace('carries the accent stroke', 'declares data-focal=true').replace('carry the accent stroke', 'declare data-focal=true')
        text = text.replace('wears the accent', 'declares data-focal=true')
        text = text.replace('one-accent rule is the whole colour system of the house style', 'focal budget is independent of semantic/category colors')
        text = text.replace('"claim, and the ink ramp exists so everything else stays ranked "\n            "without spending the accent"', '"claim; semantic colors do not consume focal slots"')
        text = text.replace('ONE NON-FOCAL INK', 'ONE NON-FOCAL FILL').replace('shared ink', 'shared fill')
    if name in {'verify-ridgeline.py', 'verify-bump.py'}:
        text = re.sub(r'^ACCENTS = .*\n', '', text, flags=re.M)
        text = text.replace('"stroke", "width", "line")', '"stroke", "width", "line", "focal")')
        text = text.replace('"stroke", "width", "offset")', '"stroke", "width", "offset", "focal")')
        text = text.replace('stroke, width, line):', 'stroke, width, line, focal=False):')
        text = text.replace('stroke, width, offset):', 'stroke, width, offset, focal=False):')
        text = text.replace('        self.stroke = stroke\n', '        self.stroke = stroke\n        self.focal = focal\n')
        text = text.replace('    @property\n    def focal(self):\n        return self.stroke in ACCENTS\n\n', '')
        text = text.replace('width, line))', 'width, line, attrs.get("data-focal", "").lower() == "true"))')
        text = text.replace('width, match.start()))', 'width, match.start(), attrs.get("data-focal", "").lower() == "true"))')
        text = text.replace('carry the accent stroke', 'declare data-focal=true')
        text = text.replace('stroke weight agreeing with stroke colour', 'stroke weight agreeing with focal metadata')
        text = text.replace('mismatch between colour and weight', 'mismatch between focal metadata and weight')
        text = text.replace('colour and weight sends', 'focal metadata and weight sends')
    if name == 'verify-service-blueprint.py':
        start = text.index('    # The accent is what the reader sees')
        end = text.index('\ndef ', start)
        text = text[:start] + '    # Semantic colors may repeat on any cell without implying focal status.\n\n' + text[end:]
        text = text.replace('5. FOCAL — at most one `data-focal="true"` cell, and no other row mark\n   painted with the accent.', '5. FOCAL — at most one `data-focal="true"` cell; semantic colors may repeat.')
        text = re.sub(r'^ACCENT_RE = .*\n', '', text, flags=re.M)
    if name == 'verify-heatmap.py':
        text = re.sub(r'def _is_accent\(.*?(?=def _parse_color)', '', text, flags=re.S)
        text = re.sub(r'                elif _is_accent\([^\n]+\n                    focal = True\n', '', text)
        text = text.replace('        cells.append(\n', '''        palette = {(30, 41, 59), (59, 130, 246), (245, 158, 11),
                   (34, 197, 94), (168, 85, 247), (236, 72, 153)}
        if focal:
            palette |= {(219, 234, 254), (254, 243, 199), (209, 250, 229),
                        (243, 232, 255), (252, 231, 243)}
        if raw_rgb not in palette and errors is not None:
            errors.append("heatmap fill must use a semantic palette hue or neutral ink")

        cells.append(
''')
        text = text.replace('"opacity": opacity,', '"opacity": opacity,\n                "rgb": raw_rgb,')
        text = text.replace('    if non_focal:\n', '''    if non_focal:
        if len({c["rgb"] for c in non_focal}) > 1:
            errors.append(f"{path.name}: non-focal cells must share one hue for a comparable opacity ramp")
''')
        text = text.replace('2. MONOTONE FILL', '2. MONOTONE SHARED-HUE FILL')
        text = re.sub(r'3\. ONE FOCAL MAX.*?(?=\n\d\.)', '3. ONE FOCAL MAX — at most one cell declares data-focal="true".\n   Color alone never makes a cell focal.\n', text, flags=re.S)
    if name == 'verify-waterfall.py':
        text = re.sub(r'^ACCENT_STROKES = .*\n', '', text, flags=re.M)
        text = text.replace('"stroke", "index")', '"stroke", "index", "focal")')
        text = text.replace('fill: str, stroke: str) -> None:', 'fill: str, stroke: str, focal: bool = False) -> None:')
        text = text.replace('        self.stroke = stroke\n', '        self.stroke = stroke\n        self.focal = focal\n')
        text = text.replace('attrs.get("fill", ""), attrs.get("stroke", ""))', 'attrs.get("fill", ""), attrs.get("stroke", ""),\n                attrs.get("data-focal", "").lower() == "true")')
        text = text.replace('bar.stroke.lower() in ACCENT_STROKES', 'bar.focal')
        text = text.replace('paper_match[1].lower() if paper_match else None', 'paper_match[1].lower() if paper_match else "#ffffff"')
        text = text.replace('def check_sign_treatment(', '''def color_rgba(value: str) -> tuple | None:
    """Resolve the palette's hex and rgb/rgba paints, plus SVG white."""
    value = re.sub(r"\\s+", "", value.lower())
    if value == "white":
        value = "#ffffff"
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(c * 2 for c in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return (*[int(value[i:i+2], 16) for i in (1, 3, 5)], 1.0)
    match = re.fullmatch(r"rgba?\\(([^)]+)\\)", value)
    if match:
        try:
            parts = tuple(float(v) for v in match[1].split(","))
        except ValueError:
            return None
        if len(parts) == 3:
            parts += (1.0,)
        if len(parts) == 4 and all(0 <= v <= 255 for v in parts[:3]) and 0 <= parts[3] <= 1:
            return parts
    return None


def outline_contrast(stroke: tuple, paper: tuple) -> float:
    """WCAG contrast of a palette outline composited over the canvas."""
    def luminance(rgb):
        values = [v / 255 for v in rgb[:3]]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
        return sum(w * v for w, v in zip((0.2126, 0.7152, 0.0722), linear))
    visible = tuple(stroke[3] * c + (1 - stroke[3]) * bg for c, bg in zip(stroke[:3], paper[:3]))
    a, b = luminance(visible), luminance(paper)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def check_sign_treatment(''')
        start = text.index('    # Absolute check:')
        end = text.index('    rises =', start)
        text = text[:start] + '''    # Keep tinted increases and hollow decreases independently of hue.
    # Focal bars retain the existing exemption; signed labels and geometry
    # still identify their direction.
    tints = {"#dbeafe", "#fef3c7", "#d1fae5", "#f3e8ff", "#fce7f3",
             "rgba(100,116,139,0.15)"}
    strokes = {"#3b82f6", "#f59e0b", "#22c55e", "#a855f7", "#ec4899",
               "#1e40af", "#b45309", "#166534", "#6b21a8", "#9d174d",
               "#64748b", "#1e293b"}
    tints = {color_rgba(color) for color in tints}
    strokes = {color_rgba(color) for color in strokes}
    background = color_rgba(paper)
    for bar in bars:
        stroke = color_rgba(bar.stroke)
        if stroke is not None and background is not None and outline_contrast(stroke, background) < 3:
            errors.append(f"{bar.label}: outline contrast must be at least 3:1; use the role's dark counterpart")
        if bar.role != "delta" or id(bar) in focal_set:
            continue
        fill = color_rgba(bar.fill)
        valid_fill = fill in tints if bar.value > 0 else fill == background
        if not valid_fill or stroke not in strokes:
            errors.append(f"{bar.label}: increases require a semantic tint and decreases "
                          "require hollow paper, both with a contrasting palette stroke")
''' + text[end:]
        text = text.replace('rises = {bar.fill for bar in bars', 'rises = {color_rgba(bar.fill) for bar in bars')
        text = text.replace('falls = {bar.fill for bar in bars', 'falls = {color_rgba(bar.fill) for bar in bars')
        text = text.replace('sorted(rises)', 'sorted(rises, key=repr)').replace('sorted(falls)', 'sorted(falls, key=repr)')
    text = text.replace('one accent', 'one focal').replace('One accent', 'One focal')
    return text
