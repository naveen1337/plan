# Stack

Default stack unless the project explicitly requires otherwise.

## Versions / packages

- `react`, `vite`, `typescript` (strict mode)
- `tailwindcss` + app-specific `tailwind.config.js`
- shadcn/ui blocks — base UI kit (Button, Input, Dialog, Select, Form, Table, etc.)
- `react-router-dom` — all client routing lives under `src/routes/`
- `@reduxjs/toolkit`, `react-redux` — slices in `src/store/`, DevTools enabled in dev
- `@tanstack/react-query` — server state
- `@tanstack/react-table` — tables; filtering, searching (globalFilter), sorting, pagination ALWAYS externally controlled
- `zod` — the only validation library
- `@sinclair/typebox` + `json-schema` (`zod-to-json-schema` or equivalent) — schema generation only
- `echarts` + `echarts-for-react` — the only chart library
- `@uiw/react-codemirror` (+ `@codemirror/*` extensions) — the only code editor
- `lucide-react` — the only icon library

## Rules

1. Do not introduce another icon library when Lucide can provide the icon.
2. Prefer TypeScript types over `any`. Use `unknown` + narrowing at boundaries (e.g. remote parsing) if the shape is uncertain.
3. Prefer typed Redux hooks throughout:
   ```ts
   // store/hooks.ts
   import { useDispatch, useSelector } from "react-redux";
   import type { AppDispatch, RootState } from "./store";

   export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
   export const useAppSelector = useSelector.withTypes<RootState>();
   ```
4. Enable Redux DevTools by default in development (RTK does this automatically unless explicitly disabled — do not disable it).
5. Use TanStack Table for any non-trivial table behavior instead of hand-rolling sort/filter/pagination.
6. TanStack Table MUST be fully controlled — never rely on uncontrolled internal defaults:
   ```tsx
   // Screen owns ALL table state (local useState, Redux, or URL search params)
   const [sorting, setSorting] = useState<SortingState>([]);
   const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
   const [globalFilter, setGlobalFilter] = useState("");
   const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 20 });

   const table = useReactTable({
     data, columns,
     state: { sorting, columnFilters, globalFilter, pagination },
     onSortingChange: setSorting,
     onColumnFiltersChange: setColumnFilters,
     onGlobalFilterChange: setGlobalFilter,
     onPaginationChange: setPagination,
     getCoreRowModel: getCoreRowModel(),
     getFilteredRowModel: getFilteredRowModel(),
     getSortedRowModel: getSortedRowModel(),
     getPaginationRowModel: getPaginationRowModel(),
     manualPagination: true, // when server-paginating
     pageCount, // required with manualPagination
   });
   ```
   - Filtering, searching (`globalFilter`), sorting, pagination state lives in Screen (or Redux/URL for shareable state), passed down to UI/table components as props.
   - Server-driven tables: use `manualFiltering/manualSorting/manualPagination` + Query keys derived from the controlled state.
   - UI/table components receive `table` instance or state + callbacks via props; they never own the source of truth.
7. Zod is the ONLY validation library — never introduce Yup, Joi, Valibot, or hand-rolled validators:
   - Colocate schemas as `<name>.schema.ts` (page) or `shared/schemas/` (reused).
   - Validate forms (with `@hookform/resolvers/zod` + `react-hook-form` on shadcn Form), URL params, filter state, and `remote/` responses (`schema.parse` / `safeParse` at the boundary).
   ```ts
   // pages/users/user.schema.ts
   import { z } from "zod";
   export const userFilterSchema = z.object({
     query: z.string().max(100).default(""),
     status: z.enum(["active", "invited", "suspended"]).default("active"),
     page: z.coerce.number().int().min(0).default(0),
     pageSize: z.coerce.number().int().min(1).max(100).default(20),
   });
   export type UserFilters = z.infer<typeof userFilterSchema>;
   ```
8. TypeBox + JSON Schema are ONLY for schema generation (dynamic/config-driven forms, generated docs, API contracts):
   - Use TypeBox `Type.Object(...)` / JSON Schema as the generative source, then derive runtime validation (Zod or TypeBox `Value.Check`) from that single source — never maintain two divergent schemas by hand.
   - `utils/` may hold pure schema-transform helpers (TypeBox ↔ JSON Schema ↔ Zod); validation execution stays in Screen/forms/`remote/`.
9. Apache ECharts is the ONLY chart library — never introduce Recharts, Chart.js, Victory, Nivo, or others:
   - Wrap in `shared/components/Chart.tsx` (ECharts-for-React, app theme, loading/empty/error slots, autoresize).
   - Chart `option` objects are config: build them in `_ctrl.ts` (pure builder functions of data) or page `components/*_chart_option.ts`. Screen fetches data via Query and passes it down; UI renders `<Chart option={...} />`.
10. CodeMirror is the ONLY editor for code/text editing surfaces — never introduce Monaco, Ace, or other editors:
    - Wrap in `shared/components/CodeEditor.tsx` over `@uiw/react-codemirror` (language extension, theme matching app, `readOnly`, `basicSetup` props).
    - Screen owns `value` + `onChange`; UI receives them as props. Large docs: debounce onChange in Screen.
11. shadcn/ui blocks are the base UI kit — do not hand-roll Button/Input/Dialog/Select/Table/Form duplicates and do not introduce MUI, AntD, Chakra, or other component libraries:
    - Compose pages as `Screen → UI → shadcn primitives + page components (Filters/Table/Dialog/EmptyState)`.
    - Shared wrappers in `shared/components/` extend shadcn primitives with app tokens, never fork divergent copies.
