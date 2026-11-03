# Cadence Skills

Five skills built by the Cadence team. [Preview the output](https://github.choosecadence.com) before downloading.

- **Decision Engine Builder**: pulls your decision-making out of your head and turns it into a scoring system you can automate.
- **Advanced Skill Creator**: lets you build, test, and ship Claude skills without starting from scratch each time.
- **Check Skill Security**: helps you verify that the skills you're installing are safe.
- **Site Security Audit**: scans your live deployed app for exposed credentials, missing auth, and misconfigurations.
- **CC-Viz**: transforms terminal output into diagrams and visual reports so you can see exactly what your agents are doing.

---

## Installation

Pick the method that matches how you're running Claude.

### Claude Desktop

Open Settings, click **Customize**, then **Add Marketplace**. Paste this URL:

```
https://github.com/Cadence-Intelligence/skills.git
```

After install, skills activate on their own. No slash command needed.

### Claude Code CLI

Either download from the [releases page](https://github.com/Cadence-Intelligence/skills/releases) and tell your agent to copy the contents into `~/.claude/skills/<skill-name>`, or register the marketplace and install per skill:

```bash
/plugin marketplace add https://github.com/Cadence-Intelligence/skills.git

/plugin install decision-engine-builder@cadence
/plugin install advanced-skill-creator@cadence
/plugin install check-skill-security@cadence
/plugin install site-security-audit@cadence
/plugin install cc-viz@cadence
```

---

## Skills

| Skill | What it does |
|-------|-------------|
| [decision-engine-builder](decision-engine-builder/) | Interviews you about how you actually prioritize, builds a scoring model, connects it to your tools |
| [advanced-skill-creator](advanced-skill-creator/) | Create, test, and distribute Claude skills with a self-correcting Architect path |
| [check-skill-security](check-skill-security/) | Static security analysis for `.skill` files and folders: prompt injection, exfiltration, obfuscation, supply chain |
| [site-security-audit](site-security-audit/) | Security audit for live, deployed web apps: secrets in JS bundles, unauthenticated endpoints, misconfigurations |
| [cc-viz](cc-viz/) | Turn terminal output into styled HTML pages: diagrams, diff reviews, data tables, slide decks |

---

## What Each Skill Does

### Decision Engine Builder

Extract your invisible decision-making through conversation and turn it into an automated scoring system.

**Activates when:** You want to prioritize, automate a recurring decision, or build a triage system.

**Example usage:**

"Help me prioritize my task list"
"Build me a triage system"
"Automate how I decide what to work on"

- Quick Mode: 5 questions, 5 minutes, 80% of the value
- Deep Mode: full extraction (guilt curves, hidden rules, overflow patterns, protected slots)
- Works with any tool: Todoist, Notion, Asana, ClickUp, Google Sheets, Gmail, plain text
- Always delivers a working system on Day 1

---

### Advanced Skill Creator

Create, test, and distribute Claude skills. Five-minute drafts to fully evaluated, packaged skills with self-correcting quality loops.

**Activates when:** You want to build a skill, turn a workflow into something reusable, or package and test an existing skill.

**Example usage:**

"Build me a skill for this workflow"
"Turn this into something reusable"
"I want a comprehensive skill with quality guardrails"

- 5 paths: Draft (5 min) · Draft+Test (15 min) · Full Eval (30 min) · Architect (1-2 hrs) · Package
- Architect path: generate, grade, extract patterns, iterate until quality stabilizes
- Rubric-based grading with explicit PASS/FAIL criteria per dimension
- Ships with `validate_skill.py` and `package_skill.py`

---

### Check Skill Security

Audit any skill file before you install it. Pass a `.skill` archive, a folder path, or anything from the marketplace and get a structured security report.

**Activates when:** You want to verify a skill is safe before installing it, especially from an untrusted source.

**Example usage:**

"Is this skill safe to install?"
"Audit this .skill file before I add it"
"Check this before I install it"

- Six audit phases: prompt injection, data exfiltration, obfuscation, supply chain, persistence, tool poisoning
- Invisible Unicode injection detection (U+E0000-U+E007F, invisible to humans, readable by LLMs)
- Four severity levels: CLEAR / REVIEW / CAUTION / BLOCK
- Standalone scanner: `python3 scripts/audit.py /path/to/skill` (exit codes: 0=CLEAR, 1=REVIEW, 2=CAUTION, 3=BLOCK)

---

### Site Security Audit

Security audit for deployed web apps. Give it a URL and it auto-detects the stack, then runs targeted checks.

**Activates when:** You want to audit a live site, check if your deployed app is secure, or find exposed credentials and missing auth.

**Example usage:**

"Audit this URL for security issues"
"Is my Vercel app secure?"
"Find vulnerabilities in my deployed site"

- Auto-detects: Vercel, Supabase, Cloudflare Workers, Firebase, Next.js, Nuxt, Hono, Express
- Seven phases: secrets in JS bundles, API auth, CRUD without auth, input validation, security headers, dependencies, sensitive data exposure
- Stack-specific fix guides for Supabase, Cloudflare Workers, Better Auth

---

### CC-Viz

Turn complex terminal output into styled HTML pages that open in the browser. Architecture diagrams, diff reviews, data tables, slide decks: all self-contained files, no build step.

**Activates when:** You ask for a diagram, architecture overview, diff or plan review, or are about to receive a complex table in the terminal.

**Example usage:**

"Draw a diagram of our authentication flow"
"Give me an architecture overview"
"/diff-review"
"/plan-review ~/docs/refactor-plan.md"

- 11 diagram types: Mermaid for connections (flowcharts, sequences, ER, state machines), CSS Grid for architecture, HTML tables for data, Chart.js for dashboards
- Proactive: auto-converts complex tables (4+ rows or 3+ columns) to HTML without being asked
- Six slash commands: `/diff-review`, `/plan-review`, `/generate-slides`, `/project-recap`, `/generate-web-diagram`, `/fact-check`
- Anti-slop enforcement: forbidden fonts, colors, and layout patterns baked in

---

## Release Download

Download individual `.skill` files from the [v1.0 release](https://github.com/Cadence-Intelligence/skills/releases/tag/v1.0):

```bash
curl -L -o decision-engine-builder.skill \
  "https://github.com/Cadence-Intelligence/skills/releases/download/v1.0/decision-engine-builder.skill"

unzip decision-engine-builder.skill -d ~/.claude/skills/
```

Same pattern for the others. Claude Code picks up the new skill in the running session.

## Manual

```bash
git clone https://github.com/Cadence-Intelligence/skills.git
cd skills
./install.sh                           # all skills
./install.sh decision-engine-builder   # or one at a time
./install.sh advanced-skill-creator
./install.sh check-skill-security
./install.sh site-security-audit
./install.sh cc-viz
```

---

## License

[CC BY-NC 4.0](LICENSE). Cadence Intelligence, 2026. Free to share and adapt with attribution; commercial use requires permission.
