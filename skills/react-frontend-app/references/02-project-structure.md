# Project Structure

General structure. Adjust root layout when needed, but keep separation of responsibilities.

```text
src/
├── pages/
│   └── <page-name>/
│       ├── <page-name>_screen.tsx
│       ├── <page-name>_ui.tsx
│       ├── <page-name>_ctrl.ts
│       ├── <page-name>.schema.ts (Zod schemas, page-scoped)
│       ├── types.ts (optional, page-scoped only; prefer z.infer from schema)
│       └── components/
│           ├── user_table.tsx
│           ├── user_filters.tsx
│           └── user_dialog.tsx
├── shared/
│   ├── components/   # shadcn-based reusable presentation + Chart.tsx (ECharts) + CodeEditor.tsx (CodeMirror)
│   ├── controllers/  # reusable cross-page behavior
│   ├── schemas/      # shared Zod schemas (reused validation)
│   ├── utils/        # pure functions only (incl. pure schema transforms)
│   └── helpers/      # side-effectful reusable ops
├── remote/           # HTTP boundary, only raw fetch() location
├── types/            # app-wide shared types (api.ts, user.ts, auth.ts, ...)
├── store/            # Redux Toolkit slices + typed hooks
├── routes/           # React Router definitions
└── main.tsx
```

## Placement rules

| What | Where |
|---|---|
| Page orchestration/rendering/config | `pages/<name>/` |
| Component used by one page | `pages/<name>/components/` |
| Component used by ≥2 pages | `shared/components/` |
| Type used by one page | `pages/<name>/types.ts` |
| Type shared app-wide | `types/` |
| Pure computation | `shared/utils/` |
| I/O, storage, logging, HTTP helpers | `shared/helpers/` |
| Raw fetch, headers, timeouts, error mapping | `remote/` |
| Slices, store setup | `store/` |
| Route objects, guards, lazy imports | `routes/` |

Do not place globally reusable components inside a page directory. Promote them on second use.
