---
title: Skills Index
type: index
description: Entry point to all agent skills in this repository, with links to each skill and its reference documents.
skills_count: 2
---

# Skills Index

Skills are reusable markdown instructions. Load the `SKILL.md` for a task area first, then the linked references for deeper detail.

---

## 1. Python Backend

- **Skill:** [python-backend/SKILL.md](python-backend/SKILL.md)
- **Use when:** creating or changing backend routes, modules, services, database access, config, auth, background jobs, external API calls, or backend tests.
- **Stack:** Python 3.13, FastAPI, uv, ruff, Postgres, Redis, Pydantic v2.

### References

- [01 - Stack and Tooling](python-backend/references/01-stack.md)
- [02 - Project Structure](python-backend/references/02-project-structure.md)
- [03 - Layer Contracts](python-backend/references/03-layers.md)
- [04 - Data Access](python-backend/references/04-data-access.md)
- [05 - Config, Security, External I/O, Logging, Jobs](python-backend/references/05-config-security-io.md)
- [06 - Testing and Quality](python-backend/references/06-testing-quality.md)

---

## 2. React Frontend App

- **Skill:** [react-frontend-app/SKILL.md](react-frontend-app/SKILL.md)
- **Use when:** creating pages, components, routing, client or server state, tables, forms, validation, schemas, charts, code editing, or styling.
- **Stack:** React, Vite, TypeScript (strict), Tailwind, shadcn/ui, Redux Toolkit, TanStack Query/Table, Zod.

### References

- [01 - Stack](react-frontend-app/references/01-stack.md)
- [02 - Project Structure](react-frontend-app/references/02-project-structure.md)
- [03 - Page Architecture: Screen / UI / Controller](react-frontend-app/references/03-page-architecture.md)
- [04 - Shared Layers: Components, Controllers, Utils, Helpers, Types](react-frontend-app/references/04-shared-layers.md)
- [05 - Remote and State: fetch boundary, Query, Redux](react-frontend-app/references/05-remote-state.md)
- [06 - Styling, Components, Naming, Dependencies](react-frontend-app/references/06-styling-conventions.md)
