---
name: react-frontend-app
description: Build React + Vite + TypeScript + Tailwind frontend apps using Screen/UI/Controller page architecture, Redux Toolkit, TanStack Query/Table (externally controlled), React Router, Zod validation, TypeBox/JSON Schema generation, Apache ECharts, CodeMirror, shadcn/ui blocks, and Lucide icons. Use when creating pages, components, routing, client or server state, tables, forms, validation, schemas, charts, code editing, or styling in this stack.
license: MIT
compatibility: opencode, claude-code
metadata:
  stack: react vite typescript tailwind
  audience: frontend-developers
  workflow: react-page-architecture
---

# React Frontend App

Opinionated skill for React + Vite + TypeScript + Tailwind CSS applications.

## When to use

Use this skill when the task involves, in a React/Vite/Tailwind project:

- Creating a new page, dialog, table, filter, or form
- Adding routing, client state, or server-state fetching
- Creating or promoting a shared component, util, helper, or type
- Styling with Tailwind or editing `tailwind.config.js`
- Reviewing frontend code for layering violations

If the project explicitly uses a different stack, follow the project and ignore conflicting defaults here.

## Core stack (defaults)

- React + Vite + TypeScript (strict, prefer types over `any`)
- Tailwind CSS + app-specific `tailwind.config.js`
- shadcn/ui blocks for all base UI (Button, Input, Dialog, Table, Form, etc.) — do not hand-roll duplicates or introduce another component library
- React Router DOM for routing (`routes/`)
- Redux Toolkit for client/app state, DevTools enabled in development
- TanStack Query for server state (GET, mutations, cache, invalidate)
- TanStack Table for tables — filtering, searching (global filter), sorting, pagination MUST be externally controlled state (Screen/Redux/URL), never uncontrolled internal defaults
- Zod as the only validation library — all forms, filters, params, and remote payloads validate via Zod
- TypeBox + JSON Schema for schema generation (dynamic forms, config-driven UI, API contracts) — derive Zod ↔ JSON Schema from a single source where possible
- Apache ECharts (`echarts`, `echarts-for-react`) as the only chart library — never introduce Recharts, Chart.js, Victory, or others
- CodeMirror (`@uiw/react-codemirror`) as the only code/text-editing surface — never introduce Monaco, Ace, or other editors
- Lucide React as the only icon library — never introduce another icon lib

Details: [references/01-stack.md](references/01-stack.md)

## Mandatory project structure

```text
src/
├── pages/<page-name>/
│   ├── <page-name>_screen.tsx
│   ├── <page-name>_ui.tsx
│   ├── <page-name>_ctrl.ts
│   ├── types.ts (only if page-scoped)
│   └── components/
├── shared/components/ | controllers/ | utils/ | helpers/
├── remote/
├── types/
├── store/
├── routes/
└── main.tsx
```

Rules: page-only components stay in `pages/<name>/components/`; promote to `shared/components/` only when reused. Page-only types stay in the page; app-wide types go in `types/`.

Details: [references/02-project-structure.md](references/02-project-structure.md)

## Page architecture (Screen / UI / Controller)

Every substantial page uses three files:

- `<name>_screen.tsx` — orchestration only (behavior)
- `<name>_ui.tsx` — rendering only (pure function of props)
- `<name>_ctrl.ts` — local config, constants, reducers, mocks (no I/O)

Workflow for any new or changed page:

1. Define page config in `_ctrl.ts` (page size, defaults, options, validation config).
2. Implement behavior in `_screen.tsx` (Redux, Query, handlers, navigation, loading/error states).
3. Implement rendering in `_ui.tsx` (props in, JSX out, no hooks with side effects).
4. Split rendering into page `components/` (e.g. `user_table.tsx`, `user_filters.tsx`, `user_dialog.tsx`).

Full contracts + examples: [references/03-page-architecture.md](references/03-page-architecture.md)

## Layer rules (enforce strictly)

- UI must NOT: call APIs, use Redux/Query, hold app state, `useEffect`, navigate, access global state, or cause side effects.
- Screen owns: state, selectors/dispatches, Query, API interaction, effects, memos/callbacks, handlers, navigation, permissions, transforms, loading/error handling.
- Controller must NOT: perform HTTP, DB, storage, or any I/O.
- `utils/` = pure functions only (input → output, deterministic, no mutation of externals).
- `helpers/` = side effects / I/O (HTTP, storage, files, analytics, logging).
- `remote/` is the only place that calls raw `fetch()`. Flow: `Screen → TanStack Query → Remote API → remote/ → fetch()`.
- Dependency direction: `Screen → Controller → Shared/Helpers/Remote → Utils`. UI never reaches upward into Redux/API/Remote.

Details: [references/04-shared-layers.md](references/04-shared-layers.md), [references/05-remote-state.md](references/05-remote-state.md)

## State ownership (smallest scope wins)

```text
Local UI-only state → Page Controller → Redux Toolkit → TanStack Query
```

- Local `useState`/`useReducer` for UI-only state.
- Redux Toolkit slices + `useAppDispatch()` / `useAppSelector()` for shared client state (auth, theme, prefs, global UI, cross-page workflows).
- TanStack Query for server state — do NOT copy it into Redux without a clear requirement.
- Never create global state for single-component state.

Details: [references/05-remote-state.md](references/05-remote-state.md)

## Styling, components, naming

- Tailwind for all styling; define colors, typography, spacing, radius, shadows, breakpoints as semantic tokens in `tailwind.config.js` (e.g. `bg-background text-foreground`), never repeat hardcoded theme values.
- shadcn/ui blocks as the base component set; compose page UI from `Filters/Table/Dialog/EmptyState` built on shadcn primitives.
- Charts: Apache ECharts only, via a small shared wrapper (theme, loading/empty states, resize handling). Chart option objects live in `_ctrl.ts` or page `components/chart_option.ts`, data fetching stays in Screen.
- Code editing: CodeMirror only. Wrap in a shared `CodeEditor.tsx` (theme, language extension, readOnly/diff handling); Screen owns value + onChange, UI renders it as a prop.
- Validation: Zod only (`*.schema.ts` colocated with page or in `shared/schemas/`); TypeBox/JSON Schema only for generation-driven use cases.
- Tables: TanStack Table with fully controlled state — `state: { columnFilters, globalFilter, sorting, pagination }` + `onXChange` handlers owned by Screen (local state, Redux, or URL search params). Never rely on uncontrolled defaults.
- Prefer small composable components: `Screen → data/handlers → UI → Filters/Table/Dialog/EmptyState`.
- Names: `users_screen.tsx`, `users_ui.tsx`, `users_ctrl.ts`, `user_table.tsx`. Avoid generic `common.ts` / `misc.ts` unless scope is genuine.
- Shared components (`Button.tsx`, `Input.tsx`, `Modal.tsx`, etc.) expose behavior via props, contain no app business logic, use Lucide icons.

Details: [references/06-styling-conventions.md](references/06-styling-conventions.md)

## Pre-completion checklist

Before finishing, verify:

1. UI file contains no Redux, Query, fetch, `useEffect`, navigation, or business logic.
2. No raw `fetch()` outside `remote/`.
3. No side effects in `utils/`; no pure-only logic hidden in `helpers/`.
4. Server state in Query, not duplicated in Redux; no overscoped global state.
5. Reusable components/types promoted to `shared/` / `types/`; page-only code kept in page.
6. Icons from `lucide-react` only; TypeScript strict with minimal `any`.
7. Validation via Zod only; no Yup/Joi/Valibot. Schema generation via TypeBox/JSON Schema only.
8. Charts via Apache ECharts only; no Recharts/Chart.js/Victory. Editors via CodeMirror only; no Monaco/Ace.
9. Base UI from shadcn/ui blocks only; no second component library.
10. TanStack Table filtering/searching/sorting/pagination fully controlled by external state (Screen/Redux/URL) — no uncontrolled table defaults driving app behavior.
