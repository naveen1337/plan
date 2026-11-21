# Styling, Components, Naming, Dependencies

## Tailwind + shadcn/ui

- All styling via Tailwind; keep an app-specific `tailwind.config.js` defining the design system: colors, typography, spacing, radius, shadows, breakpoints, component tokens.
- shadcn/ui blocks are the base kit: build all Button/Input/Select/Dialog/Form/Table/EmptyState UI on shadcn primitives + Tailwind tokens. No second component library, no hand-rolled duplicates.
- Prefer semantic tokens over repeated arbitrary values:

```tsx
// good
<div className="bg-background text-foreground">
// avoid
<div className="bg-[#0a0a0a] text-[#ededed]">
```

## Component design

One responsibility per component. Avoid the god-page anti-pattern (API + Redux + state + logic + table + dialogs + forms + rendering in one file).

Prefer:

```text
Screen (data, state, handlers)
└── UI (props only)
    ├── Filters
    ├── Table
    ├── Dialog
    └── EmptyState
```

## Naming

- Pages: `users_screen.tsx`, `users_ui.tsx`, `users_ctrl.ts`
- Page components: `user_table.tsx`, `user_filters.tsx`, `user_dialog.tsx`
- Schemas: `user.schema.ts` (Zod, page) or `shared/schemas/*.schema.ts` (reused)
- Charts: `*_chart.tsx` (renders shared `<Chart/>`) + `*_chart_option.ts` or ctrl `build*Option()` (pure ECharts option builders)
- Editors: render shared `<CodeEditor/>` (CodeMirror); no per-page editor forks
- Avoid generic `common.ts` / `helper.ts` / `misc.ts` / `utils.ts` unless the file genuinely represents that scope — prefer descriptive names.

## Charts (Apache ECharts only)

- Never introduce Recharts, Chart.js, Victory, or others. All charts go through `shared/components/Chart.tsx` (echarts-for-react, app theme, loading/empty/error, autoresize).
- Options are pure config: build in `_ctrl.ts` or `*_chart_option.ts` from data passed as args. Screen fetches via Query, UI renders. No fetching or Query inside chart components.

## Code editing (CodeMirror only)

- Never introduce Monaco, Ace, or other editors. All code/text editing goes through `shared/components/CodeEditor.tsx` (`@uiw/react-codemirror`).
- Screen owns `value`/`onChange` (debounce large docs, validate with Zod where applicable); UI receives them as props. Theme/language extensions via props with app defaults.

## Dependency direction

```text
Page Screen → Page Controller → Shared Controllers / Helpers / Remote → Utilities
```

UI never reaches upward: no `UI → Redux`, `UI → API`, `UI → Remote`. Screen orchestrates infrastructure; UI renders props.
