# Remote + State: fetch boundary, Query, Redux

## `remote/` — the only HTTP boundary

Centralize: request creation, methods, headers, payload serialization, response parsing, `AbortController`/cancellation, timeouts, HTTP error handling, auth headers.

Flow: `Screen → TanStack Query → Remote API → remote/ → fetch()`. Never call raw `fetch()` in Screens, UI, controllers, or helpers outside `remote/`.

Validate at the boundary with Zod (only validation lib): every `remote/` response is parsed via its Zod schema (`parse`/`safeParse`) before returning to Query. Map failures to typed errors.

```ts
// remote/client.ts
export type RequestOptions = RequestInit & { timeoutMs?: number };

export async function request<T>(url: string, options?: RequestOptions): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(),
    options?.timeoutMs ?? 15_000,
  );
  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...options?.headers },
    });
    if (!res.ok) throw new RemoteError(res.status, await res.text());
    return (await res.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}
```

```ts
// remote/users.ts — Zod-validated boundary
import { z } from "zod";
import { request } from "./client";

export const userSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  status: z.enum(["active", "invited", "suspended"]),
});
export type User = z.infer<typeof userSchema>;

export async function fetchUsers(): Promise<User[]> {
  const raw: unknown = await request("/api/users");
  return z.array(userSchema).parse(raw); // always validate remote payloads
}
```

## Schema generation (TypeBox + JSON Schema)

Use TypeBox/JSON Schema ONLY for generation-driven cases (dynamic/config-driven forms, generated docs, contract exchange). Keep one source of truth: define the schema once (TypeBox `Type.*` or a Zod schema), derive the other artifact (`zod-to-json-schema`, `typebox-to-zod`, or `Value.Check`) — never hand-maintain parallel Zod + TypeBox copies. Pure schema transforms may live in `utils/`; execution (parse/validate) stays in Screen/forms/`remote/`.

## TanStack Query — server state

Use for GETs, mutations, caching, refetching, loading/error states, invalidation. Screens consume `useQuery`/`useMutation`; `remote/` performs the actual fetch.

- Table/chart/editor server state: derive Query keys from externally controlled state (Zod-validated filters, pagination, chart params). Example: `["users", filters]` where `filters = userFilterSchema.parse(searchParams)`.
- ECharts data and CodeMirror document content fetched via Query; mutations invalidate and update cache — never stash server snapshots in Redux or uncontrolled component state.

Do NOT copy server data into Redux unless there is a clear app requirement (e.g. offline editing draft that outlives the cache).

## Redux Toolkit — client/app state

Use for cross-area shared state: auth, prefs, theme, app config, global UI, persistent cross-page workflows. Slices in `store/`; consume via `useAppDispatch()` / `useAppSelector()`.

DevTools: keep enabled in development (RTK default — do not disable).

## State ownership priority

```text
Local UI-only state → Page Controller → Redux Toolkit → TanStack Query
```

Use the smallest scope that works. No global state for single-component state. No Redux copy of Query-cached server state.
