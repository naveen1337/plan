# Page Architecture: Screen / UI / Controller

## Screen (`<name>_screen.tsx`) — orchestration layer

May contain: page/app state, Redux selectors + dispatches, TanStack Query, API interaction, `useEffect`/`useMemo`/`useCallback`, event handlers, navigation, business logic, permission checks, data transforms, error/loading handling, communication between controllers and UI.

Owns all behavior. Prepares all data + callbacks the UI needs.

```tsx
// pages/users/users_screen.tsx
import { useUsersQuery } from "@/remote/users";
import { useAppDispatch } from "@/store/hooks";
import { UsersUI } from "./users_ui";

export function UsersScreen() {
  const users = useUsersQuery();
  const dispatch = useAppDispatch();

  const handleCreateUser = () => {
    // page behavior (e.g. open dialog, navigate, dispatch)
  };

  const handleDeleteUser = (id: string) => {
    // page behavior (e.g. mutate + invalidate)
  };

  return (
    <UsersUI
      users={users.data ?? []}
      loading={users.isLoading}
      onCreateUser={handleCreateUser}
      onDeleteUser={handleDeleteUser}
    />
  );
}
```

## UI (`<name>_ui.tsx`) — rendering only

Must: render components, receive data/callbacks via props, compose visuals, apply Tailwind classes, render loading/empty/error states supplied by Screen.

Must NOT: call APIs, use Redux, use TanStack Query, hold app state, contain business logic, use `useEffect`, navigate, access global state, or cause side effects. Be a pure function of props as far as possible. Local presentational `useState` (e.g. disclosure toggle inside a dumb component) is acceptable only if it never drives app behavior — otherwise lift it to Screen.

```tsx
// pages/users/users_ui.tsx
import type { User } from "./types";

type UsersUIProps = {
  users: User[];
  loading: boolean;
  onCreateUser: () => void;
  onDeleteUser: (id: string) => void;
};

export function UsersUI({ users, loading, onCreateUser, onDeleteUser }: UsersUIProps) {
  if (loading) return <div className="text-muted">Loading users…</div>;
  if (users.length === 0) return <div className="text-muted">No users found.</div>;

  return (
    <div>
      <button className="btn-primary" onClick={onCreateUser}>
        Create User
      </button>
      {users.map((user) => (
        <UserRow key={user.id} user={user} onDelete={() => onDeleteUser(user.id)} />
      ))}
    </div>
  );
}
```

## Controller (`<name>_ctrl.ts`) — local config

Use for: page constants, local state definitions, reducers for complex local state, initial state, mock data, option lists, validation config, controller functions.

- Validation config = Zod schemas (or re-exports of `<name>.schema.ts`). Never Yup/Joi/Valibot.
- Chart config = pure ECharts `option` builder functions of data (no fetching, no hooks).
- Table defaults (pageSize, sortable/filterable columns, default sorting/filters) live here, but the live table state itself is owned by Screen (see controlled-table pattern below).

Do NOT: perform HTTP, storage, or any side effects. Not a second API layer. For reusable behavior prefer Redux Toolkit or `shared/controllers/`.

```ts
// pages/users/users_ctrl.ts
import { userFilterSchema } from "./user.schema";
import type { EChartsOption } from "echarts";

export const usersPageCtrl = {
  defaultPageSize: 20,
  filters: {
    defaultStatus: "active" as const,
    statusOptions: ["active", "invited", "suspended"] as const,
  },
  filterSchema: userFilterSchema, // Zod = only validation lib
  mockUsers: [],
};

export function usersFilterReducer(state: FilterState, action: FilterAction): FilterState {
  // pure local reducer logic
  return state;
}

// Pure ECharts option builder — data in, option out. No hooks, no fetch.
export function buildUsersChartOption(usersPerDay: { day: string; count: number }[]): EChartsOption {
  return {
    xAxis: { type: "category", data: usersPerDay.map((d) => d.day) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: usersPerDay.map((d) => d.count) }],
  };
}
```

## Page components (`pages/<name>/components/`)

Strictly page-specific. Examples: `user_table.tsx` (TanStack Table wiring fed by Screen props — fully controlled, no internal state as source of truth), `user_filters.tsx` (shadcn Form + Zod), `user_dialog.tsx` (shadcn Dialog), `user_chart.tsx` (shared `<Chart/>` ECharts wrapper + ctrl option builder), `user_editor.tsx` (shared `<CodeEditor/>` CodeMirror wrapper, value/onChange via props). Move to `shared/components/` once a second page needs them.

Controlled-table contract: Screen owns `sorting / columnFilters / globalFilter / pagination` (useState, Redux, or URL search params validated by Zod) and passes state + `onXChange` down. Server-driven tables use `manual*` flags + Query keys derived from that state. Page `user_table.tsx` receives the table instance or state/callbacks as props and only renders (shadcn Table primitives).
