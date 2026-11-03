"""Technical-diagram density guidance and structural validation."""
import re


TECHNICAL_TYPES = {
    'architecture', 'architecture-delta', 'it-state', 'flowchart', 'sequence',
    'state', 'er', 'swimlane', 'nested', 'tree', 'org-chart', 'layers',
    'high-level', 'process', 'medallion', 'data-flow', 'dp-integration',
    'dp-security-matrix', 'deployment', 'dependency', 'uml-class', 'db-schema',
}


def guidance(name, text):
    if name == 'SKILL.md':
        text = re.sub(r'^\*\*Target density:.*$',
                      'Keep implementation-critical components, conditions and relationships. Review density using §7.', text, flags=re.M)
        text = text.replace('The pattern owns semantic primitives and its tighter budget; the type owns layout grammar.',
                            'The pattern owns semantic primitives; the type owns layout grammar. Content counts follow §7.')
        text = text.replace("- If you're past the complexity budget (§7), split into an overview + detail.",
                            '- Split into overview + detail when separate views improve readability (§7).')
        text = text.replace('anything the complexity budget (§7) will force out', 'any planned grouping or omissions')
        start = text.index('### Complexity budget (per diagram)')
        end = text.index('\n---', start)
        text = text[:start] + '''### Complexity budget (per diagram)

| Guideline | Use |
|---|---|
| Overview | Aim for 5–9 nodes |
| Density review | Above 9 nodes or 12 connectors, check grouping and routing |
| Large diagrams | Above 24 nodes, assess overview + detail |
| Focal elements / annotation callouts | Max 2 each |

Size technical diagrams for the content and intended display. Group by responsibility; enlarge the canvas when the display supports it. Split when labels or routes remain crowded. Preserve implementation-critical components, conditions and relationships.

Per-type guidance: [layout-budget.md](references/layout-budget.md#complexity-budget-per-diagram). Apply connector, semantic and quantitative-encoding rules at every size.
''' + text[end:]
        text = text.replace("- [ ] Within the type's complexity budget (§7)?",
                            '- [ ] Required content preserved; labels and routes readable at the intended size (§7)?')

    elif name == 'layout-budget.md':
        text = re.sub(r'^Routed from.*$', 'Routed from SKILL.md §7. Technical content counts and depth values are planning guides; retain semantic structure, focal limits and quantitative encodings.', text, flags=re.M)
        text = re.sub(r'^These are the per-type limits\..*$',
                      'Use these counts to review grouping and readability at the intended display size (SKILL.md §7).', text, flags=re.M)
        rows = text.splitlines()
        for index, row in enumerate(rows):
            if any(f'({kind})' in row for kind in (
                    'architecture delta', 'architecture containment', 'sequence',
                    'swimlane', 'ER', 'nested', 'layer stack', 'deployment',
                    'dependency', 'UML class', 'db schema')) or re.match(r'\| Max (?:tree|org chart)', row):
                rows[index] = row.replace('| Max ', '| Suggested ', 1)
        text = '\n'.join(rows)
        text = text.replace('| Suggested combined fragments (sequence) | 1 (default); 2 only if each is single-region `opt`/`loop` |',
                            '| Suggested combined fragments (sequence) | Start with 1; add as needed for control flow |')
        text = text.replace('| Suggested unique components / relationships / ledger entries (architecture delta) | 8 / 10 / 8 |',
                            '| Suggested components / relationships (architecture delta) | 8 / 10; ledger covers every change |')
        text = text.replace('If you exceed, split into two diagrams (overview + detail).',
                            'Split by subsystem or phase when separate views improve readability.')

    elif name == 'output-spec.md':
        start = text.index('How much of the source survives.')
        end = text.index('\n---', start)
        text = text[:start] + '''Choose content for the diagram's purpose.

| Level | What survives |
|---|---|
| `faithful` | Every distinct component and relationship; merge only exact duplicates. |
| `balanced` (default) | Components and relationships needed to explain the subject; aggregate incidental detail. |
| `simplified` | Capabilities and their sequence; retain boundaries and conditions that affect meaning. |

Apply SKILL.md §7 for density. Use labeled zones for useful responsibility or trust boundaries. A large source may remain one diagram when its labels and routes are readable at the intended size.

### Simplification

Remove decoration, merge identical replicas, then consider leaf clusters or incidental infrastructure. Preserve distinct behavior, failure paths and trust boundaries. In `faithful`, keep distinct content across detail diagrams if needed. Report material grouping or omissions (§5).
''' + text[end:]
        text = text.replace('Detail sets *how many*; audience sets *what they\'re called*.',
                            'Detail selects content; audience sets wording.')
        text = re.sub(r'^Any time output is smaller than input.*$',
                      'Report merged, collapsed or omitted content after the file path. Short and specific:', text, flags=re.M)
        text = re.sub(r'## 5\. Fidelity ledger.*?(?=\n---)',
                      '## 5. Content coverage\n\nReport material grouping or omissions alongside the SVG, including which components or relationships they affect.\n', text, flags=re.S)
        text = text.replace('- [ ] Fidelity ledger reported for anything cut?',
                            '- [ ] Material grouping or omissions reported?')
        text = text.replace("- [ ] Node count inside the detail level's ceiling?\n- [ ] `faithful` above 9 nodes → zoned, and split above 24?",
                            '- [ ] Detail matches the request; grouping, labels and routes remain readable at the intended size?')

    elif name == 'semantic-patterns.md':
        text = text.replace('**Complexity budget:**', '**Layout guidance:**')
        text = re.sub(r'^\*\*Layout guidance:\*\* Tree\'s own.*$',
                      '**Layout guidance:** Keep parent-child structure traceable. Split by subsystem when needed for readability, retaining stable IDs and parent context in each file. Show at most one in/out port-label pair per block; keep constraints and assumptions in metadata.', text, flags=re.M)
        text = text.replace('Aggregate excess sources as a named cohort.',
                            'Aggregate sources only when their behavior is equivalent.')
        text = text.replace('Split lifecycle overview from dense guard logic once either ceiling is reached.',
                            'Separate dense guard logic when it obscures the lifecycle.')
        text = text.replace('4–5 ordered phase states;', 'ordered primary phase states;')
        text = text.replace('and type-specific limits.', 'and type-specific guidance.')
        text = re.sub(r'^- Apply the stricter of.*$',
                      '- Content counts follow SKILL.md §7; preserve the pattern\'s required semantics, including distinct failure and terminal outcomes.', text, flags=re.M)

    elif name.removeprefix('type-').removesuffix('.md') in TECHNICAL_TYPES:
        # Count recommendations stay near their geometry; emphasis caps stay binding.
        text = re.sub(r'(?m)^(\| |\- )Max (?!focal|side callouts|highlighted cycles)', r'\1Suggested ', text)
        text = text.replace('| Dimension | Max |', '| Dimension | Guidance |')
        replacements = {
            '**Diamond** — decision (≤3 exits)': '**Diamond** — decision; label every exit',
            '- Decision diamond with 4+ exits — refactor into nested diamonds.':
                '- Decision branches too crowded to distinguish; separate decisions only when the logic supports it.',
            '| `alt` | **2 max** | dashed horizontal hairline across the frame | `[guard]` on region 1; `[else]` (or a second guard) on region 2 |':
                '| `alt` | 2 or more | dashed horizontal hairline between regions | Explicit `[guard]` per region; optional `[else]` last |',
            '**Budget** (tightens Architecture\'s flat 3-zone cap; see `layout-budget.md`): ≤2 administrative bands, ≤4 traffic scopes, ≤8 nodes, 2 focal elements. Split per subscription when a figure exceeds that.':
                '**Layout guidance:** Start with 2 administrative bands, 4 traffic scopes and 8 nodes; expand as needed under SKILL.md §7. Keep at most 2 focal elements.',
            '- Max 3 **flat** zones per diagram. More and it reads like a swimlane (use that type instead). Nested administrative and traffic scopes under **Containment** below are not this cap — they nest, so the cap is sibling traffic scopes at one level.':
                '- Start with 3 flat zones; add zones when they represent distinct responsibilities or trust boundaries.',
            '- **Budget:** at most **8 unique components**, **10 unique relationships**, and **8 ledger entries** across the complete comparison. A retained ID counts once, not once per snapshot. A component that is both changed and moved consumes two ledger entries. Split larger migrations into named subsystems or phases; never drop edges to fit.':
                '- **Density review:** Start with 8 unique components and 10 relationships across the comparison. Keep every change covered in the ledger; split by subsystem or phase when crowded.',
            'drawn relationship endpoints, budgets, and exact ledger coverage.':
                'drawn relationship endpoints and exact ledger coverage.',
            '- Nested fragments: **max 1 level**. Prefer two separate diagrams over deep nesting.':
                '- Prefer shallow fragment nesting; separate paths when frames obscure message order.',
            '- Default: **one** fragment per diagram. A second only if both stay under the complexity budget.':
                '- Use the fragments needed to express guards and repetition; keep their boundaries readable.',
            '- Suggested combined fragments: 1 (hard default); 2 only if each is a single-region `opt`/`loop`.':
                '- Prefer one combined fragment; add fragments when needed for the control flow.',
            'If you exceed, split: overview (happy path) + detail (failure / refresh path).':
                'Separate happy and failure paths when one view becomes crowded; retain their guards and outcomes.',
            '- Nested `alt` inside `alt` (split into two diagrams).':
                '- Nested fragments whose guards or message order cannot be followed.',
            '- Suggested depth: 4 (root + 3 tiers). Max breadth per level: 5.':
                '- Start with 4 levels and 5 nodes per level; expand while ancestry remains easy to follow.',
            '- Tree 5+ levels deep on a single page (illegible — split).':
                '- Deep or wide trees whose ancestry cannot be followed at the intended size.',
            '- More than 6 levels (information disappears inward).':
                '- Nested levels with too little space for labels and content.',
            '- Suggested visible org nodes: 12. If more, create an overview org chart plus separate detail charts per pod.':
                '- Start with 12 visible org nodes; split by team when crowded.',
            '- Suggested direct reports under one parent: 5. If there are more, introduce grouping nodes.':
                '- Above 5 direct reports, review spacing; grouping must reflect actual ownership.',
            'Over budget → split into one deployment diagram per environment.':
                'Split by environment when placement and network paths become hard to follow.',
            "Over budget: collapse a leaf cluster into one aggregate node labelled with its count (e.g. `+6 leaves`), and say so in a caption — don't silently drop nodes.":
                'Aggregate equivalent leaf nodes only when individual dependencies are incidental; report the grouping.',
            'Max 5 tables, max 8 column rows shown per table, max 6 FK edges, max 2 focal elements. Over budget → show the subsystem, not the database, and say so in a caption.':
                'Start with 5 tables, 8 rows per table and 6 FK edges; expand for required schema detail. Keep FK endpoints visible. Split by subsystem when crowded; max 2 focal elements.',
            'when a table has more columns than the budget allows':
                'when incidental columns are omitted',
            'Max 7 classes, max 8 relationships, max 5 members per compartment (overflow becomes a `sublabel`-role `…` line), max 2 focal elements. Over budget → split by package.':
                'Start with 7 classes, 8 relationships and 5 members per compartment; retain members needed to explain behavior. Mark omitted members with `…`. Split by package when crowded; max 2 focal elements.',
            'Seven is the ceiling rather than the target. Three compartments per box makes a class diagram dense fast, so treat 4–5 classes as the normal size; the illustrative example uses all seven only because it doubles as the legend for the full relationship vocabulary.': '',
            'Above 4 lanes or 6 steps: split into two diagrams (e.g., ingestion pipeline / analytics pipeline).':
                'Above 4 lanes or 6 steps, review spacing and handoffs; split by pipeline when crowded.',
            'Above 6 lanes or 12 steps: split into two diagrams (overview + detail).':
                'Above 6 lanes or 12 steps, review spacing and handoffs; split by phase when crowded.',
            '- **More than 12 steps without splitting** — use an overview + detail pair.':
                '- Steps packed too tightly to follow their order and handoffs.',
            '- **More than 6 roles** — split into two matrices (e.g., human roles vs service accounts) before exceeding 6 columns.':
                '- Role columns too narrow to read; widen the canvas or separate role groups.',
            '- **More than 14 components** — split by domain (storage / compute / observability / governance) before exceeding 14 rows.':
                '- Component rows too dense to compare; separate domains when needed.',
            'This is the one type where the default 9-node / 12-arrow budget is intentionally exceeded. A realistic platform integration shows:':
                'A platform integration may need:',
            '## 10. Budget — this type exceeds the default': '## 10. Density',
            '- **> 16 total components or > 5 per zone.** Density cap; split into two diagrams.':
                '- **Crowded zones.** Review grouping above 16 components or 5 per zone; split when labels or paths cannot be followed.',
            'Caps at 4 sources; for more, split into a separate diagram.':
                'Start with 4 sources; expand the layout for distinct sources.',
            '**Max 3 outgoing edges per node.** Above 3, introduce a hub (usually the `focal` node). The chevron banner is the legend; if a node is fanning out to four downstream targets, it\'s secretly the hub — make it explicit.':
                '**Fan-out:** Above 3 outgoing edges, review port spacing and routing. Add a hub only when the system has one.',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
    return text


def runtime(name, text):
    if name == 'verify-architecture-containment.py':
        text = re.sub(r'^MAX_(?:ADMIN|TRAFFIC|NODES) = \d+\n', '', text, flags=re.M)
        start = text.index('    admin_count = sum(')
        end = text.index('    known_scopes = set(scopes)', start)
        text = text[:start] + text[end:]
    elif name == 'verify-architecture-delta.py':
        text = re.sub(r'    component_ids = .*\n', '', text)
        text = re.sub(r'    if len\((?:component_ids|relationship_ids)\) > \d+:\n        fail\(root, "[^"]*budget[^"]*"\)\n', '', text)
        text = text.replace('if not entries or len(entries) > 8:', 'if not entries:')
        text = text.replace('ledger budget requires 1-8 entries', 'ledger requires at least one entry')
    return text
