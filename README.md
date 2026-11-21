# Plan and Execution

A web interface for **planning tasks with AI and executing them with AI**.

Write a plan as structured markdown — clear **requirements**, **objectives**, **implementation guidelines**, and **guardrails** — then hand that plan to an AI agent to fulfill. The same workflow applies to any productivity task: coding, report generation, research, documentation, or anything in between.

## The idea

AI outputs are only as good as the instructions they receive. Instead of typing ad-hoc prompts, this tool lets you:

1. **Plan** — author a task as a structured markdown document (requirements, objectives, guidelines, guardrails).
2. **Attach skills** — link reusable markdown "skills" (conventions, playbooks, constraints) that the AI must follow while executing.
3. **Execute** — send the plan + skills to an AI agent and track its progress.
4. **Review** — inspect the output, iterate on the plan, and re-run.

The plan document is the single source of truth. It is human-readable, versionable, and portable — paste it into any AI tool.

## What it's for

| Use case | Example plan |
|---|---|
| **Coding** | "Build a user settings page" with stack rules, layer rules, and a completion checklist |
| **Report generation** | "Generate a quarterly sales report" with data sources, format, tone, and forbidden claims |
| **Generic productivity** | "Draft a project proposal", "Refactor a module", "Summarize research" — any task you can describe |

## Plan document format

Plans are plain markdown with conventional sections. The tool scaffolds them; the AI consumes them.

```markdown
# Task: <one-line summary>

## Objectives
- What "done" looks like, measurable where possible.

## Requirements
- MUST / SHOULD / MAY statements. Inputs, outputs, constraints.

## Implementation Guidelines
- Steps, architecture notes, libraries to use, files to touch.

## Guardrails
- Things the AI must NOT do (no scope creep, no new dependencies, no destructive ops).
- Stop conditions and when to ask a human.

## Skills
- skill:react-frontend-app
- skill:report-writing

## Acceptance Criteria
- [ ] Checkable outcomes used to verify the result.
```

### Skills

Skills are **markdown files** (with optional YAML frontmatter, e.g. `skills/<name>/SKILL.md`) that encode reusable knowledge:

- Tech stack defaults and conventions
- Coding standards and architecture rules
- Writing styles and report templates
- Checklists the agent must pass before finishing

When a plan references a skill, the executor loads it into the AI's context alongside the plan. See [`skills/react-frontend-app/SKILL.md`](skills/react-frontend-app/SKILL.md) for an example.

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────┐
│   Frontend (React)  │  HTTP  │   Backend (FastAPI)      │
│                     │ ─────▶ │                          │
│  - Plan editor      │  JSON  │  - Plans API (CRUD)      │
│  - Skills library   │        │  - Skills API            │
│  - Execution view   │ ◀────  │  - Execution runner      │
│  - Review & diff    │  SSE   │  - AI agent integration  │
└─────────────────────┘        └──────────────────────────┘
```

- **Frontend — React** (Vite + TypeScript + Tailwind): plan editor, skill library, execution dashboard.
- **Backend — Python FastAPI**: plan/skill storage and API, validation, execution orchestration, streaming agent output (SSE).
- **Storage**: plans and skills are markdown files on disk (git-friendly). No database required for v1.
- **AI integration**: provider-agnostic adapter (start with one LLM provider; the plan text stays portable).

## Project structure

```
plan/
├── README.md
├── AGENTS.md              # Instructions for AI agents working on / using this repo
├── backend/               # FastAPI application (planned)
│   ├── app/
│   │   ├── core/          # Shared infrastructure (config, errors, db, security)
│   │   └── modules/       # One folder per business module
│   │       └── <name>/    # <name>_ctrl, _service, _helper, _utils, _schema
│   └── tests/
│       ├── core/
│       └── modules/<name>/
├── frontend/              # React application (planned)
│   └── src/
├── plans/                 # Saved plan documents (markdown)
└── skills/                # Skill library (markdown, SKILL.md format)
    └── react-frontend-app/
```

## Getting started

```bash
# Backend
cd backend
uv sync                      # or: pip install -e .
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Roadmap

- [ ] Plan CRUD API + markdown scaffolding (FastAPI)
- [ ] Skill library browsing + attaching skills to plans
- [ ] Plan editor with section templates and validation
- [ ] Execution runner with streaming agent output
- [ ] Output review (diffs for code tasks, preview for reports)
- [ ] Plan versioning and re-runs
- [ ] Export plan for use in external AI tools

## Contributing

Read [`AGENTS.md`](AGENTS.md) before making changes — it defines the conventions for this repository and the rules an AI agent must follow when executing plans produced by this tool.
