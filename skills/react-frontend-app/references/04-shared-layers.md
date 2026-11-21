# Shared Layers: Components, Controllers, Utils, Helpers, Types

## `shared/components/` — reusable presentation

Examples: shadcn/ui-based `Button.tsx`, `Text.tsx`, `Modal.tsx`, `Dialog.tsx`, `Input.tsx`, `Select.tsx`, `Card.tsx`, plus app wrappers `Chart.tsx` (Apache ECharts) and `CodeEditor.tsx` (CodeMirror).

- Base all primitives on shadcn/ui blocks; no second component library (no MUI/AntD/Chakra), no hand-rolled duplicates of shadcn blocks.
- No app-specific business logic; behavior via props.
- Icons via `lucide-react` only.
- No Redux, Query, fetch, or navigation inside.
- No duplicate app-wide versions of standard components.
- `Chart.tsx`: single ECharts-for-React wrapper (app theme, loading/empty/error slots, autoresize). Page charts pass `option` built by pure ctrl builders.
- `CodeEditor.tsx`: single CodeMirror wrapper (`@uiw/react-codemirror`, language/theme/`readOnly` via props). Screen owns value + onChange.

## `shared/controllers/` — reusable behavior

Coordinates cross-page state/behavior (e.g. `useDialogController`, `usePaginationController`). Not a dumping ground: page-specific logic stays in the page's `_ctrl.ts`; unrelated logic gets separate files.

## `shared/utils/` — pure functions only

Each function: accepts input, returns output, no side effects. Must NOT: HTTP, DB, browser storage, global-state access, external mutation.

```ts
export function formatCurrency(value: number, currency = "INR"): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(value);
}
```

Prefer deterministic functions. Anything performing I/O belongs in `helpers/`.

## `shared/helpers/` — side effects / I/O

HTTP operations, browser storage, file ops, external services, analytics, logging. Mental model: `utils = pure computation`, `helpers = side effects`. Never hide side effects inside a util.

## `types/` vs page `types.ts`

- `types/` (e.g. `api.ts`, `user.ts`, `auth.ts`, `navigation.ts`, `common.ts`): genuinely shared app-wide types.
- `pages/<name>/types.ts`: types used by one page only.
- Validation source of truth: Zod schemas (`<name>.schema.ts` per page, `shared/schemas/` when reused) — infer TS types via `z.infer`. TypeBox/JSON Schema only where generation is required (dynamic forms, contracts); keep a single source and derive the rest.

Do not move every type global. Promote on second use.
