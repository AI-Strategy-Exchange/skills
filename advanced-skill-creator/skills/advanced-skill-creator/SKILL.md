---
name: advanced-skill-creator
description: >
  Create, test, package, and distribute Claude Code skills. Use whenever the user
  wants to build a skill from scratch, turn a recurring prompt or workflow into a
  reusable skill, stop copy-pasting the same instructions, make a workflow run
  consistently across future sessions, edit or improve an existing SKILL.md,
  package a skill folder for sharing, zip a skill as a .skill archive, ship a
  skill to teammates, test whether a skill triggers or works end-to-end, or
  tune a skill description so it fires on the right queries. Fires for phrases
  like "turn this into a skill", "make this a skill", "package this skill",
  "distribute this skill", "make claude remember this workflow", "reuse this
  prompt", "share this skill". For reference-heavy skills that produce creative
  or generative output (HTML, documents, designs, copy) where quality varies
  across runs, use the Architect path.
license: CC BY-NC 4.0
metadata:
  author: cadence
  version: "1.1"
---

# Skill Creator

Create, test, and distribute skills — from a 5-minute draft to a fully
evaluated, packaged skill. Follows the Agent Skills standard.

The simplest use is just Steps 1–2: capture intent, write a SKILL.md, save
it to `~/.claude/skills/<name>/`, and you're done. Everything after Step 2
(testing, packaging, description optimization, Architect) is optional and
only pulled in when the user asks.

## Pick your path

| Path | When to use |
|------|-------------|
| **Draft only** | User wants a working SKILL.md fast, no testing |
| **Draft + test** | User wants to verify the skill works before using it |
| **Full eval** | User wants baseline comparisons, metrics, and description optimization |
| **Package existing** | User has a skill folder and just wants to distribute it |
| **Architect** | Deep skill with references, templates, anti-patterns, and self-correction loop. Use for skills that produce creative/generative output (HTML, documents, designs, copy) where quality varies across runs. |

### Confirm the path with the user (mandatory when ambiguous)

If the request clearly maps to one path (e.g. *"package this skill"* → Package,
*"optimize the trigger description"* → Full eval), proceed — don't ask a pointless
question. Otherwise **use the `AskUserQuestion` tool** with these options so the
user picks explicitly:

```
question: "Which path should I take?"
multiSelect: false
options:
  - label: "Draft only"     description: "Write the SKILL.md and install it. ~5 minutes."
  - label: "Draft + test"   description: "Draft, then run it on a few prompts side-by-side."
  - label: "Full eval"      description: "Structured eval + description optimization loop."
  - label: "Package existing" description: "Validate and zip an existing skill folder."
  - label: "Architect"      description: "Deep skill with rubric, anti-patterns, iterative loop. Slower."
```

Do not silently default. If `AskUserQuestion` is unavailable, ask in plain text
and wait for the user to answer before drafting.

**Auto-suggest Architect when** the request matches any of:
- The skill produces HTML, documents, copy, designs, or other creative output
- The user mentions "comprehensive", "high-quality", "like cc-viz", "detailed"
- The user wants anti-patterns, quality guardrails, or aesthetic guidelines
- Output quality would vary significantly across runs without guardrails

Surface Architect as the default option in the `AskUserQuestion` call when
these conditions match, but still let the user override.

### Checkpoints (always show the user before committing)

At each of these points, present what you have and wait for confirmation before
moving on. Don't write files to `~/.claude/skills/` (or anywhere else durable)
until the user has seen and approved them:

1. **After intent capture** — recap "here's what I understood" in 2–4 bullets
   before drafting.
2. **Before saving the SKILL.md** — show the full draft (frontmatter + body)
   in a fenced block and ask "save this as-is, or iterate?"
3. **After test runs** — show with-skill vs baseline outputs side-by-side and
   ask for feedback before revising.
4. **Before packaging or installing globally** — show the final folder layout
   and install path and ask for approval.

For heavier eval paths (Full eval, Architect), outputs go into a workspace
folder and the `eval-viewer` HTML UI becomes the visual review surface —
see Step 3 "Reviewing and iterating" and [references/advanced-eval.md](references/advanced-eval.md).

### Who grades the output? (script / hybrid / judgment)

Before running any eval round, decide per-dimension how it gets graded. The
rubric needs a `grading:` tag on every dimension. Three values:

| Tag | Meaning | Grader | Example |
|---|---|---|---|
| **`script`** | Fully mechanical — regex, word count, list lookup, schema validation | Auto-graded by a small script in-session, no human needed | "No em dashes appear", "Output is valid JSON", "≤ 1000 words" |
| **`hybrid`** | Script catches the obvious failures, judgment grades the rest | Script first (gates out the cheap fails), then judgment for what's left | "Length in band AND opener is a claim not setup" — length is script, opener-quality is judgment |
| **`judgment`** | No mechanical shortcut; must be read by a grader | LLM-as-judge IF the criteria are domain-neutral (formatting consistency, presence of structure); otherwise **the human** via eval-viewer | "Sounds like the user's voice", "Feels intentional", "Palette works for the brand" |

**Routing rule:** if any `judgment` dimension requires user-specific taste
(voice, design, brand, "does this sound like me") the eval round MUST end at
the eval-viewer so the user reviews outputs and writes notes into
`feedback.json` — those notes ARE the grade. LLM-as-judge is only acceptable
for domain-neutral judgment dimensions (e.g. "is the heading hierarchy
logical"), never for user-taste dimensions.

The Architect Phase 2 (rubric design) and Phase 5 (grade) sections enforce
this — every dimension must carry the `grading:` tag and Phase 5 routes by it.

---

## Skill format reference

```
skill-name/              ← directory name must match frontmatter `name`
├── SKILL.md             ← required
├── scripts/             ← optional; executable code
├── references/          ← optional; docs loaded on demand
└── assets/              ← optional; templates, fonts, static files
```

### Frontmatter (required fields)

```yaml
---
name: kebab-case-name       # max 64 chars; [a-z0-9-] only; no leading/trailing hyphens
description: >              # max 1024 chars; this is the triggering mechanism
  What it does and when to use it.
license: CC BY-NC 4.0       # optional; any SPDX identifier or custom string
compatibility: Requires...  # optional; max 500 chars
metadata:                   # optional; arbitrary key-value pairs
  author: example-org
  version: "1.0"
---
```

The `name` must match the parent directory name.

### Claude Code fields (optional)

Claude Code reads more frontmatter than the open standard defines. These are
the ones that matter most; the full list is at
https://code.claude.com/docs/en/skills#frontmatter-reference.

```yaml
when_to_use: Trigger phrases or example requests.  # appended to description in the listing
disable-model-invocation: true   # Claude never loads it on its own; runs only via /name
user-invocable: false            # hidden from the / menu; only Claude loads it
argument-hint: "[env]"           # shown after /name in the menu
allowed-tools: Bash(git status *) Read   # string or YAML list; patterns allowed
paths: src/**/*.ts               # only activate for matching files
model: sonnet                    # model to run the skill on
effort: low                      # effort level while the skill runs
```

claude.ai and the Skills API may reject Claude Code-only fields, so check
before uploading a skill there.

### Installation locations

| Scope | Path |
|-------|------|
| User-level | `~/.claude/skills/` |
| Project-level | `.claude/skills/` |
| Plugin-bundled | `<plugin>/skills/` |

---

## Step 1 — Capture intent

Extract answers from the current conversation first — only ask what you can't infer:

- What should this skill help the agent do?
- When should it activate? (what user phrases or contexts)
- What does a good output look like?
- Who starts it? If it should run only when the user asks by name (deploys,
  sends, posts, reports, anything with side effects or a fixed occasion), set
  `disable-model-invocation: true`. The skill then stays out of the listing
  Claude reads every turn and is still available as `/name`.

If the user says "turn this into a skill," extract the workflow from the
conversation: tools used, step sequence, corrections made. Confirm before writing.

---

## Step 2 — Write the SKILL.md

### The description is the most important part

The description is the only thing the agent reads before deciding whether to load
the skill. Write it as an instruction, not a label. List concrete situations and
phrasings where the skill applies.

**Weak:** `"Helps with PDF files."`

**Strong:** `"Extract text, fill forms, and merge PDFs. Use when the user wants to
work with .pdf files, mentions forms or document extraction, or says things like
'read this file' or 'fill in this template.'"`

### Three-level loading

1. **Listing entry**: `name` plus `description` and `when_to_use`, always in
   context for every skill Claude can invoke on its own. Claude Code cuts each
   entry at 1,536 characters, and the whole listing shares a budget of about 1%
   of the context window. When the listing overflows, the least-used skills
   lose their descriptions first and show only their names, so they stop
   triggering. Put the key use case in the first sentence and keep the entry
   short; a 1,024-character description costs about 250 tokens on every turn.
2. **SKILL.md body** (<500 lines / ~5k tokens): loads when skill activates
3. **Referenced files**: load on demand only when needed

Keep core workflow in SKILL.md. Move large reference material to `references/`.
Point to files clearly, including *when* to read them.

### Writing style

- Use imperative form: "Run the script" not "The script should be run"
- Explain the *why* behind instructions — agents follow reasoning better than commands
- Provide a clear default, then mention alternatives briefly
- For exact output formats, provide a template
- Add a **Gotchas** section for non-obvious facts the agent will get wrong without being told

### Calibrating specificity

Match prescription level to task fragility:

- **High freedom**: multiple valid approaches → explain the goal, let agent decide
- **Medium freedom**: preferred pattern exists → pseudocode or parameterized script
- **Low freedom**: fragile operation, consistency critical → exact script, few params

### Common patterns

**Sequential checklist** (helps agent track progress):
```markdown
- [ ] Step 1: Analyze the form (`scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate (`scripts/validate.py`) — fix errors, re-validate until clean
```

**Validation loop** (agent self-corrects):
```markdown
1. Do the work
2. Run `scripts/validate.py output/`
3. If it fails, fix the issues and re-run. Only proceed when it passes.
```

**Variant dispatch** (loads only what's needed):
```markdown
Read the relevant reference before proceeding:
- AWS → `references/aws.md`
- GCP → `references/gcp.md`
```

### Scripts in `scripts/`

Design for agentic use:
- No interactive prompts — accept all input via flags, env vars, or stdin
- `--help` flag with usage examples
- Clear error messages
- Structured output (JSON/CSV) to stdout; diagnostics to stderr
- Idempotent where possible — agents may retry

### Install and done (Draft-only path)

For a personal or project-local skill, save the folder and stop:

```bash
# User-level (available in every session)
mkdir -p ~/.claude/skills/my-skill
cp SKILL.md ~/.claude/skills/my-skill/

# Or project-level (only available in this repo)
mkdir -p .claude/skills/my-skill
cp SKILL.md .claude/skills/my-skill/
```

Claude Code picks up new and edited skills in the running session (run
`/reload-skills` if you created the `skills/` directory itself during the
session). Test by sending a prompt that should trigger it, or `/my-skill` for a
manual-only skill. **If that's all you need, stop here.** Steps 3–5 and the
Architect path below are only for when the user explicitly wants testing,
distribution, or description tuning.

---

## Step 3 — Test the skill (optional)

After drafting, propose 2–3 test prompts. Share them: *"Here are a few test cases
— do these look right?"* Then run them.

### Running tests

For a quick check, the simplest thing is to install the skill (see Step 2
"Install and done") and just prompt Claude — if it triggers and the output
looks right, you're done.

For a more structured comparison, produce two outputs per prompt — one with
the skill, one without — so you can see the delta. Two ways:

**Option A — delegate via the `Agent` tool** (recommended inside Claude Code):
spawn two subagents in parallel. Give each the same prompt, and tell the
with-skill one to read the `SKILL.md` first. Collect outputs and any files
they wrote to a scratch directory.

**Option B — shell out to `claude -p`:**
```bash
# With-skill: let the skill load naturally so triggering (not just
# instruction-following) is what's being tested.
claude -p "<test prompt>" > /tmp/with_skill.md 2>&1 &

# Baseline: same prompt, skill uninstalled or renamed
claude -p "<test prompt>" > /tmp/baseline.md 2>&1 &
wait
```

If parallel runs aren't practical, run sequentially — with-skill first,
then baseline. If you want to grade multiple prompts quantitatively,
jump to the Full Eval subsections below or `references/advanced-eval.md`
for the structured `<workspace>/iteration-N/eval-<slug>/...` layout.

### Reviewing and iterating

Present with-skill and baseline outputs side by side. Ask: *"How does this look?
Anything you'd change?"*

When improving based on feedback:
- Generalize — the skill will run many times on varied prompts
- Trim instructions that aren't helping; lean prompts often outperform verbose ones
- If every test run reinvented the same helper script, bundle it in `scripts/`

### Grading (for full eval path)

Read [agents/grader.md](agents/grader.md) for the grading methodology. Follow the
grader instructions yourself to evaluate each test run:

1. Define expectations (what should the output contain/accomplish?)
2. Read the output
3. Grade each expectation as PASS/FAIL with evidence
4. Critique the evals themselves (are the assertions strong enough?)
5. Save results as `grading.json`

### Blind comparison (for full eval path)

Read [agents/comparator.md](agents/comparator.md) for blind A/B comparison methodology:

1. Label outputs as A and B (randomize which is skill vs baseline)
2. Judge purely on quality without knowing which is which
3. Pick a winner with reasoning
4. Unblind and analyze using [agents/analyzer.md](agents/analyzer.md)

For full quantitative benchmarking details:
→ see [references/advanced-eval.md](references/advanced-eval.md)

---

## Step 4 — Package for distribution (optional)

Only needed when sharing the skill with others. For personal use, Step 2's
"Install and done" is all you need.

### As a folder (simplest — for sharing via Git, Drive, copy-paste)

Ship the skill directory as-is. The recipient copies it into
`~/.claude/skills/<name>/` (or `.claude/skills/<name>/` for project scope)
and it activates on the next session.

### As a Claude Code plugin (for marketplace distribution)

Wrap one or more skills in a plugin so they can be installed via
`/plugin install`. Minimal layout:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # { "name": "my-plugin", "version": "1.0", ... }
└── skills/
    └── my-skill/
        └── SKILL.md
```

Users install with `/plugin install my-plugin@<marketplace>` once the plugin
is published to a marketplace.

### As a .skill file (zip archive)

Use the bundled packager. It validates first, then zips, excluding `evals/`,
`__pycache__`, `.DS_Store`, and `node_modules`. Run it from the skill-creator
directory (so `scripts/` resolves correctly):

```bash
cd <path-to>/advanced-skill-creator
python3 scripts/package_skill.py path/to/my-skill
python3 scripts/package_skill.py path/to/my-skill ./dist   # custom output dir
```

See [scripts/package_skill.py](scripts/package_skill.py) for the full implementation.

### Installing a .skill file

```bash
unzip my-skill.skill -d ~/.claude/skills/
```

### Validate before packaging

Run the validator directly to check a skill without packaging:

```bash
cd <path-to>/advanced-skill-creator
python3 scripts/validate_skill.py path/to/my-skill
```

Install the Python dependencies once: `pip install -r scripts/requirements.txt`.

See [scripts/validate_skill.py](scripts/validate_skill.py) for the full implementation.

Checks performed:
- `name` is kebab-case, max 64 chars, matches directory name
- `description` has no angle brackets, max 1024 chars
- `description` + `when_to_use` over 1,536 chars warns (Claude Code truncates it in the listing)
- `compatibility` max 500 chars
- No keys outside the open standard and Claude Code's documented fields; Claude Code-only fields warn, since claude.ai uploads may reject them
- `disable-model-invocation` and `user-invocable` are booleans
- `allowed-tools`: string or YAML list, permission patterns such as `Bash(git add *)` allowed; MCP tools must follow `mcp__<server>__<tool>`; unrecognized tool names and unscoped `Bash` warn; warns if a declared MCP server isn't referenced in the skill body
- `agents/` directory — all files must be `.md`; referenced agent files must exist

For the exact parse Claude Code runs, also run `claude plugin validate <dir>`
(Claude Code v2.1.233+).

---

## Step 5 — Optimize the description (advanced)

If the skill isn't triggering when it should:

1. Write 10–15 test phrases (mix of should/shouldn't trigger)
2. Include near-misses — phrases that share keywords but need something different
3. Run them through `scripts/run_eval.py` (shells out to `claude -p` in parallel)
   and note whether the skill was loaded
4. Revise the description to address the pattern, not specific query wording
5. Repeat until stable, or let `scripts/run_loop.py` do the iteration for you

### Trigger eval format

```json
[
  {"query": "ok so my boss wants me to add a profit margin column to this xlsx...", "should_trigger": true},
  {"query": "write a python function that reads a csv and uploads each row to postgres", "should_trigger": false}
]
```

Good should-not-trigger queries are near-misses, not obviously irrelevant ones.

### Automated loop

Run the eval-and-improve loop end-to-end. It holds out a test set, proposes
description rewrites by shelling out to `claude -p`, and picks the
highest-scoring variant on the held-out set:

```bash
cd <path-to>/advanced-skill-creator
python3 -m scripts.run_loop \
  --eval-set path/to/trigger-eval.json \
  --skill-path path/to/my-skill \
  --max-iterations 5 \
  --verbose
```

Uses your existing Claude Code auth — the Claude Code CLI must be on `$PATH`.
Install Python deps once with `pip install -r scripts/requirements.txt`.

As an alternative to running the script directly, you can delegate the
same loop to a subagent via the `Agent` tool — pass it the skill path, eval
set, and this workflow, and collect the resulting `best_description`.

For the full optimization workflow: → [references/advanced-eval.md](references/advanced-eval.md)

---

## Architect Path — Self-Correcting Skill Builder

For skills that produce creative or generative output where quality matters and varies across runs. Read [references/architect-workflow.md](references/architect-workflow.md) for the full detailed workflow before starting.

The architect path builds skills through a **generate → grade → extract → iterate** loop that produces reference-heavy skills with anti-patterns, templates, and quality guardrails — similar to how cc-viz was built.

### Overview: The Loop

```
Phase 1: Capture intent + style examples + anti-examples
Phase 2: Design quality rubric (BEFORE writing any skill code)
Phase 3: Write draft SKILL.md (intentionally minimal)
Phase 4: Generate 3-4 real outputs on varied inputs
Phase 5: Grade each output against rubric
Phase 6: Extract patterns (from successes) + anti-patterns (from failures)
Phase 7: Create reference templates from best outputs
Phase 8: Update SKILL.md with lessons learned
Phase 9: Repeat Phases 4-8 until quality stabilizes (2-3 rounds)
Phase 10: Polish and package
```

### Phase 1 — Capture Intent (Extended)

Same as Step 1, plus these architect-specific questions:

- **Style examples:** "Show me 2-3 examples of what good output looks like" (URLs, files, screenshots)
- **Anti-examples:** "What should it NOT look like?" (generic AI output, specific bad patterns)
- **Quality dimensions:** What matters most? (accuracy, aesthetics, consistency, completeness, distinctiveness)
- **Audience:** Who sees the output? (developer, PM, client, public)

### Phase 2 — Design the Quality Rubric

**Do this BEFORE writing any skill code.** The rubric is the foundation the entire loop grades against.

Read [references/rubric-template.md](references/rubric-template.md) for the full format and adapt it to the specific skill.

**A rubric has 4-6 weighted dimensions.** Each dimension belongs to one of
three grading categories — Phase 5 routes by category:

- `script` — a regex, word count, or schema check decides PASS/FAIL alone. No human or LLM judgment.
- `hybrid` — a script catches the obvious failures; judgment grades the rest.
- `judgment` — must be read by a grader. If it requires user-specific taste (voice, brand, design), the **human** is the only valid grader (route to eval-viewer in Phase 5). Domain-neutral judgment can be LLM-graded.

The category can be expressed two ways and Phase 5 accepts either:

1. **Preferred:** an explicit `grading: script | hybrid | judgment` field on
   the dimension (machine-readable, clearest).
2. **Acceptable:** the criteria text makes the category obvious — phrases like
   "grep for X", "regex match", "word count between N and M" signal `script`;
   "reads like the user's voice", "feels intentional" signal `judgment`.

If a rubric uses option 2, Phase 5 will infer the category at grading time
from the criteria text. Don't block on schema — block on whether the routing
is unambiguous.

Example using the preferred explicit tagging:

```yaml
dimensions:
  - name: "Information Completeness"
    weight: 25
    grading: hybrid
    pass: "All requested information present. Nothing missing or truncated."
    fail: "Missing sections, placeholder text, or incomplete content."
    script_signals: "Grep for TODO/TBD/placeholder; check for sections listed in input."

  - name: "Structural Quality"
    weight: 20
    grading: judgment
    pass: "Clear hierarchy, logical flow, appropriate sections."
    fail: "Flat structure, no visual hierarchy, walls of text."

  - name: "Distinctiveness"
    weight: 20
    grading: judgment    # user-taste → routes to human via eval-viewer
    pass: "Would not be immediately identified as AI-generated."
    fail: "Generic template feel. Default fonts/colors. No design intent."

  - name: "Anti-Pattern Free"
    weight: 20
    grading: script
    pass: "None of the documented anti-patterns are present."
    fail: "Contains one or more known anti-patterns."
    script_signals: "Each anti-pattern in references/anti-patterns.md is a regex; run all."

  - name: "Cross-Run Consistency"
    weight: 15
    grading: judgment
    pass: "Quality is similar across different inputs."
    fail: "Great on some inputs, terrible on others."
```

Save the rubric to `references/quality-rubric.md` in the skill folder.

### Phase 3 — Draft SKILL.md (V1)

Write a minimal first version:
- Core workflow (what the skill does step by step)
- Basic quality guidelines
- **No references or templates yet** — those come from the loop

This is intentionally sparse. The references will be extracted from real outputs, not invented upfront.

### Phase 4 — Generate Round

Run the draft skill on 3-4 **deliberately varied** inputs:

| Input | Purpose |
|-------|---------|
| Typical/common case | Does it handle the bread-and-butter? |
| Complex/large case | Does it scale? Does quality degrade? |
| Edge case / unusual | Does it handle ambiguity gracefully? |
| Minimal input | What does it do with almost no guidance? |

Save all outputs to a workspace folder using the same layout as the full-eval
path so `aggregate_benchmark.py` and `eval-viewer/generate_review.py` can
consume them later:

```
<skill-name>-workspace/
└── iteration-N/
    └── eval-<slug>/
        └── with_skill/
            └── run-1/outputs/output.ext
```

**Speed option:** delegate generation to subagents via the `Agent` tool so
rounds can run in parallel. Keep Round 1 in-session (you need the context),
delegate Rounds 2-3.

### Phase 5 — Grade

**Route by grading category.** For each dimension, determine its category:
prefer the explicit `grading:` field if the rubric carries one; otherwise
infer `script | hybrid | judgment` from the criteria text. If a dimension's
category is ambiguous (you can't tell whether it's hybrid or pure judgment),
treat it as `judgment` and route conservatively.

The three routes:

- **`script`** — write/run a small checker (regex, word count, schema
  validation) in-session. Save its output as evidence. No human needed.
- **`hybrid`** — run the script half first to gate out obvious failures, then
  reason through the remaining judgment portion with `<thinking>` and produce
  PASS/FAIL with evidence. Document both halves in the grade.
- **`judgment`** — depends on the criteria:
  - Domain-neutral judgment (e.g. "heading hierarchy is logical", "JSON keys
    follow consistent casing") → grade in-session with `<thinking>`.
  - User-taste judgment (voice, brand, design, "sounds like me") → **do not
    auto-grade**. Launch the eval-viewer (see
    [references/advanced-eval.md](references/advanced-eval.md) §"Grade,
    aggregate, launch viewer") so the user reviews outputs and writes notes
    into `feedback.json`. Their notes ARE the grade. Wait for them to finish
    before continuing the loop.

If every dimension is user-taste judgment, skip the auto-grade step entirely
and go straight to eval-viewer. If every dimension is `script`, auto-grade
and skip the viewer. The mixed case (most skills) does both: script gates
the cheap stuff, viewer captures the taste calls.

For script and in-session judgment grading, use `<thinking>` to reason before scoring:

```xml
<thinking>
Checking "Distinctiveness" for output-1:
- Font: Uses DM Sans + Fira Code — good, not a default
- Color: Terracotta/sage palette — distinctive, earthy
- Layout: Asymmetric grid with varied card depths — shows intent
- Would I think "AI generated this"? No — the palette and asymmetry are unusual
→ PASS
</thinking>
```

Produce a structured grade card per output:

```
Output 1 (typical case): 82/100
  ✅ Information Completeness (25/25)
  ✅ Structural Quality (20/20)
  ✅ Distinctiveness (20/20)
  ❌ Anti-Pattern Free (10/20) — emoji in section headers
  ✅ Cross-Run Consistency (7/15) — first run, limited data
```

Save to `<skill-name>-workspace/iteration-N/grades.md`.

### Phase 6 — Extract Patterns

From the grades, extract two things:

**Anti-patterns (from failures):**
```markdown
### Anti-Pattern: [Name]
**What happens:** [Describe the bad output]
**Why it's bad:** [Why this signals low quality]
**Rule:** [The explicit prohibition]
**Instead:** [What to do instead, with example]
```

**Winning patterns (from successes):**
```markdown
### Pattern: [Name]
**What it does:** [Describe the technique]
**When to use:** [Context where this works]
**Example:** [Code/markup snippet]
```

Append to `references/anti-patterns.md` and `references/patterns.md`.

### Phase 7 — Create Reference Templates

Take the highest-scoring output and save it as a reference template.

**Critical rule: Templates MUST be deliberately varied.**
- If Round 1 template is dark with teal accents → Round 2 must be light with warm tones
- If Round 1 template uses Mermaid diagrams → Round 2 should use CSS Grid
- If Round 1 template is minimal → Round 2 should be information-dense

Add a comment header to each template:
```html
<!--
  Reference template: [name]
  Aesthetic: [description]
  Palette: [colors]
  Patterns used: [list from references/patterns.md]
  Deliberately different from: [other template name]
-->
```

### Phase 8 — Update SKILL.md

Based on what grading revealed:
- Add "Read the reference template before generating" instructions
- Add anti-pattern rules (summary in SKILL.md, details in references/)
- Add quality checks section
- Refine workflow with lessons learned
- Add "Read `references/anti-patterns.md` before every generation" instruction

### Phase 9 — Iterate

Repeat Phases 4-8 with the updated skill on **new inputs** (not the same ones).

**Convergence criteria (stop when ALL met):**
- Average score ≥ 75/100 across all outputs in the round
- No FAIL on any dimension in 2+ consecutive outputs
- Anti-pattern list has stabilized (no new patterns in last round)
- At least 2 varied reference templates exist

Typically 2-3 rounds. If scores aren't improving after 3 rounds, revisit the rubric — dimensions may need adjustment.

### Phase 10 — Polish & Package

Final deliverable structure:
```
skill-name/
├── SKILL.md                    ← Workflow + quality checks + anti-pattern summary
├── README.md                   ← Architecture, for maintainers
├── references/
│   ├── quality-rubric.md       ← Grading criteria
│   ├── patterns.md             ← Winning patterns with examples
│   ├── anti-patterns.md        ← Failure patterns with rules
│   └── [domain-specific].md    ← E.g., css-patterns.md, api-reference.md
├── templates/
│   ├── template-1.ext          ← Best from Round 1 (with style comment)
│   └── template-2.ext          ← Best from Round 2 (deliberately different)
└── evals/                      ← Optional: grading history for re-evaluation
    ├── iteration-1-grades.md
    └── iteration-2-grades.md
```

Put iteration workspaces outside the skill directory — `package_skill.py` only
excludes a top-level `evals/` folder, so keep ad-hoc run artifacts elsewhere
to avoid bloating the `.skill` archive.

Run Step 4 (Package) and Step 5 (Description Optimization) from the standard paths.

---

## Reference files

Read these only when the user explicitly wants the advanced path:

- [references/advanced-eval.md](references/advanced-eval.md) — Quantitative grading, benchmark viewer, blind A/B comparison
- [references/schemas.md](references/schemas.md) — JSON schemas for evals.json, grading.json, benchmark.json
- [references/architect-workflow.md](references/architect-workflow.md) — Detailed architect path workflow with prompt engineering principles
- [references/rubric-template.md](references/rubric-template.md) — Default quality rubric format and examples
- [agents/grader.md](agents/grader.md) — Instructions for evaluating assertions against outputs
- [agents/comparator.md](agents/comparator.md) — Instructions for blind A/B comparison
- [agents/analyzer.md](agents/analyzer.md) — Instructions for post-hoc "why did the winner win" analysis
