# AGENTS.md

Instructions for AI agents working on **this repository** and for agents **executing plans** produced by this tool.

Two roles, keep them separate:

1. **Builder role** — you are developing the Plan and Execution application itself (React frontend, FastAPI backend).
2. **Executor role** — you have been given a plan document produced by this tool and must fulfill it.

---

## Role 1 — Builder (developing this codebase)

### Project overview

"Plan and Execution" is a web interface to plan tasks as structured markdown (requirements, objectives, implementation guidelines, guardrails), attach reusable markdown **skills**, and hand the plan to an AI agent to execute. See `README.md`.

### Stack

| Layer     | Technology                                                        |
|-----------|-------------------------------------------------------------------|
| Frontend  | React + Vite + TypeScript + Tailwind CSS                          |
| Backend   | Python 3.13, FastAPI, Pydantic v2, uv for dependency management   |
| Storage   | Markdown files on disk (`plans/`, `skills/`)                      |
| AI        | Provider-agnostic adapter; execution output streamed via SSE      |

### Repository layout

```
plans/       saved plan documents (markdown) — data, not code
skills/      skill library — <name>/SKILL.md (+ references/)
backend/     FastAPI app: api/ (routes), services/ (logic), models/ (Pydantic), core/ (config)
frontend/    React app (follow the react-frontend-app skill, see below)
```

### Rules for building this codebase

**General**

- Read the relevant `skills/*/SKILL.md` before touching that area. `skills/react-frontend-app/` is **mandatory** for all frontend work — it defines the stack, page architecture (Screen/UI/Controller), layer rules, and state ownership.
- Backend: keep routes thin; logic in `services/`; I/O boundaries explicit; Pydantic models for every request/response; no logic in route decorators beyond validation.
- Plans and skills are **markdown files on disk**. Never introduce a database unless a plan explicitly requires one.
- Markdown parsing: use established libraries (e.g. `python-frontmatter`, `markdown-it-py`), not hand-rolled regex parsers.
- Do not commit secrets, API keys, or `.env` files.
- Every feature needs a test: pytest for backend, vitest for frontend.

**Frontend (mandatory skill: `react-frontend-app`)**

- React + Vite + TypeScript (strict), Tailwind, shadcn/ui, React Router, Redux Toolkit (client state), TanStack Query (server state), TanStack Table (fully controlled), Zod (all validation), Lucide icons, Apache ECharts (charts), CodeMirror (code editing). No substitutes.
- Page structure: `<name>_screen.tsx` (behavior), `<name>_ui.tsx` (pure rendering), `<name>_ctrl.ts` (config/constants). UI never calls APIs, Redux, or `useEffect`.
- Raw `fetch()` only inside `remote/`. `utils/` = pure functions; `helpers/` = side effects.

**Verification before finishing**

- Backend: `uv run pytest`, lint with ruff.
- Frontend: `npm run lint`, `npm run typecheck`, `npm run test`.
- Never mark work complete with failing checks.

---

## Role 2 — Executor (fulfilling a plan)

You receive a plan document structured like the template in `README.md`. Execute it as follows:

### 1. Read the whole plan before acting

Parse every section. If **Objectives**, **Requirements**, or **Acceptance Criteria** are missing or contradictory, **stop and ask** — do not guess scope.

### 2. Load referenced skills

Plans list skills under `## Skills` (e.g. `skill:react-frontend-app`). For each:

- Read `skills/<name>/SKILL.md` and any `references/` it links.
- Treat skill rules as **binding constraints**, equal in priority to the plan's guardrails.
- If a skill conflicts with the plan, the **plan wins** — but flag the conflict before proceeding.

### 3. Respect the priority order

1. Plan guardrails (hard limits — never violated)
2. Plan requirements (MUST > SHOULD > MAY)
3. Skill conventions
4. Your defaults

### 4. Guardrail protocol

- Guardrails are hard boundaries: no scope creep, no unrequested features, no new dependencies unless the plan allows it, no destructive operations, no secrets in code or commits.
- If a step would violate a guardrail, **stop** and report the conflict instead of improvising.
- Ask a human when: instructions are ambiguous, acceptance criteria can't be verified, or required access/assets are missing.
- Work only within the scope the plan defines. Adjacent improvements you notice go in a "Follow-ups" note, not into the deliverable.

### 5. Execute and verify

- Follow the Implementation Guidelines section order where sensible; deviate only with a stated reason in your final report.
- Verify against **Acceptance Criteria** one by one. Run the tests/lint/typecheck the plan (or the relevant skill) specifies.
- When finished, report:

```markdown
## Execution Report
- **Status**: complete / partial / blocked
- **Acceptance criteria**: ✅/❌ per item, with evidence (files, test output)
- **Deviations**: what differed from the plan and why
- **Follow-ups**: out-of-scope issues noticed during execution
```

- If blocked, state exactly what is missing (input, decision, access) and stop. Do not fill gaps with assumptions and present them as done.

---

## Skill authoring (for both roles)

When creating a new skill, follow the existing format:

```
skills/<skill-name>/
├── SKILL.md          # YAML frontmatter (name, description) + the core rules
└── references/       # deeper detail, linked from SKILL.md
```

- Keep `SKILL.md` under ~200 lines; push detail into `references/`.
- `description` must say **when to use** the skill so agents can select it.
- Prefer rules that are checkable ("MUST use X", "never do Y") over vague guidance.
