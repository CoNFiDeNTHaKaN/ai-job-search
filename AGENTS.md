---
framework_version: 1.0.0
---

# Agent Guidelines: AI Job Search

This workspace is structured to manage job search activities, scraper tools, CVs, cover letters, and interview preparation.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across different AI agent frameworks (Claude Code, Google Antigravity, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified thin-pointer design. All agent runtimes should load the canonical specifications and candidate profiles from the files and directories below:

1. **Personal Candidate Profile:**
   - The candidate profile, contact details, education, and target preferences are defined in [CLAUDE.md](CLAUDE.md) and the individual profile methodology files under [.claude/skills/job-application-assistant/](.claude/skills/job-application-assistant/) (specifically `01-*.md` etc.).
2. **Canonical Workflow Specifications:**
   - The step-by-step instructions and triggers for tasks (setup, scrape, rank, apply, upskill, interview) are defined in the [.claude/](.claude/) directory (specifically under `.claude/skills/` and `.claude/commands/`).
   - Do not duplicate these rules or specifications. Treat `.claude/` files as the single source of truth.
3. **Portal Search Skills:**
   - Job-portal search CLIs live under [.agents/skills/](.agents/skills/) in the portable Agent Skills format (with a `SKILL.md` per portal). Codex and Antigravity discover these automatically; the `/scrape` workflow in [.claude/skills/job-scraper/](.claude/skills/job-scraper/) orchestrates them.

## MiMo Code Integration

[MiMo Code](https://github.com/XiaomiMiMo/MiMo-Code) (an OpenCode fork) is a supported runtime for this workspace, alongside Claude Code. It reads project state from `.mimocode/`.

**Skills are not duplicated — the format is already portable, not ported.** MiMo Code natively scans `.claude/skills/**/SKILL.md` as a built-in "compatibility directory" — the same thin-pointer principle as this file. `job-application-assistant`, `job-scraper` (`/scrape`), and `upskill` (`/upskill`) work unmodified; there is nothing under `.mimocode/skills/`. Only `name`/`description`/`hidden` frontmatter keys are read by MiMo — `allowed-tools` (Claude Code-only) is ignored there and has no effect either way.

**Commands are ported, not shared.** MiMo Code has no compatibility-directory scan for commands, so the 12 command files that live at `.claude/commands/*.md` are mirrored at `.mimocode/commands/*.md` with tool names remapped to MiMo's vocabulary (`Read`/`Write`/`Edit`/`Glob`/`Grep`/`Bash`/`WebFetch`/`WebSearch` → `read`/`edit`/`glob`/`grep`/`bash`/`webfetch`/`websearch`). `$ARGUMENTS`, `$1`/`$2`/`$3`, `!command`, and `@file` all work identically in both formats, so command bodies port close to verbatim. No command was renamed — MiMo's built-in slash commands (`/connect`, `/compact`, `/details`, `/editor`, `/exit`, `/export`, `/help`, `/init`, `/models`, `/new`, `/redo`, `/sessions`, `/share`, `/themes`, `/thinking`, `/undo`, `/unshare`) do not collide with any command in this repo, and MiMo lets custom commands override built-ins anyway.

**Subagents replace Task-tool spawns with real MiMo subagents.** Where Claude Code commands spawned a `general-purpose` Agent inline (the `/apply` reviewer critique, `/rank`'s parallel batch scorers), MiMo Code uses two dedicated `mode: subagent` definitions instead:
- `.mimocode/agents/reviewer.md` — the `/apply` Step 3 hiring-manager-proxy critique (company research, factual grounding audit, structured Part A/Part B feedback). Invoked via the `task` tool with the job posting, both drafts, and company/role passed inline.
- `.mimocode/agents/rank-scorer.md` — the `/rank` Step 2 triage scorer, invoked once per ~5-job batch via the `task` tool with that batch's jobs and a compact rubric passed inline.

Both run with `write: false` / `edit: false` — they can research and score, but they cannot touch disk. This is a closer match to the original Task-tool architecture than a sequential single-session simulation would have been, since MiMo Code has genuine subagent isolation (`mode: subagent`, per-agent tool restrictions, the `task` permission key).

**Configuration.** `.mimocode/mimocode.json` mirrors the least-privilege spirit of `.claude/settings.json`: `bash` and `skill` permissions are pattern-allowlisted (`bun run *`, `python(3) salary_lookup.py *`, `pdftotext*`, `lualatex *`, `xelatex *`; only the `job-application-assistant` skill is pre-allowed), everything else falls back to MiMo's own defaults. The `provider`/`model` block points at a local `llama.cpp` server (`llamacpp/qwen3-coder-next`, OpenAI-compatible endpoint) — see the README for how to start it.

**`.claude/` stays in place.** It is not superseded — it remains the source of truth for skills (natively read by both runtimes) and lets Claude Code behavior be diffed against MiMo Code's during the transition.