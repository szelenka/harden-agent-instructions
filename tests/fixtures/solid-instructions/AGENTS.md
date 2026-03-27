# Invoice Processor

**HARD RULES — violations break the build:**
- NEVER import from `src/internal/` outside its own module
- ALL request bodies MUST be validated with a Zod schema before use
- Database changes require a Prisma migration — never modify the DB directly

## Quick Start

```bash
npm run check        # lint + format-check + test (run before every commit)
```

## Build & Test Commands

```bash
npm run build        # TypeScript compilation
npm run test         # Jest unit + integration tests
npm run lint         # ESLint
npm run format       # Prettier check (no write)
npm run check        # All of the above
npm run migrate      # Prisma migrate dev
```

## Architecture

Request flow: `route -> validate (Zod) -> service -> Prisma -> response`

- **`src/routes/`** — HTTP handlers. Parse requests, call validators, delegate to services. No business logic here.
- **`src/services/`** — Business logic. Receive validated data, return domain objects.
- **`src/validators/`** — Zod schemas, one per endpoint. Co-located with routes.
- **`src/internal/`** — Shared infra (Prisma client, structured logger). Only services may import from here.
- **`prisma/schema.prisma`** — Data model: Invoice, LineItem, Payment.

## Testing Conventions

- Test files live next to source: `invoice-service.test.ts` beside `invoice-service.ts`
- Use `jest.mock()` for Prisma — never hit a real DB in unit tests
- Integration tests in `tests/integration/` use a test database via Docker
- Name tests: `describe("InvoiceService.create")` -> `it("rejects negative amounts")`

## Codebase Conventions

- **Search before create**: grep for existing patterns before writing new code. Extend existing services over creating new files
- **Naming**: use camelCase for variables/functions, PascalCase for types/classes, kebab-case for filenames
- **Library preference**: use Zod (already adopted), Prisma, Express — avoid hand-rolling validation, DB clients, or HTTP utilities
- **Common mistakes**:
  - Running `npm install <pkg>` directly — instead, add to package.json then `npm install`
  - Putting validation logic in services — validation belongs in `src/validators/`
  - Importing `db.ts` from routes — routes must go through services

## Verification (Done Checklist)

Before considering any task complete:

1. `npm run check` passes (exit code 0)
2. No new eslint-disable comments added
3. If you added an endpoint: `grep -r "z.object" src/validators/` shows the corresponding schema file
4. If you changed the data model: `prisma migrate dev --create-only` creates a migration without errors

## Self-Improvement

When you discover a non-obvious pattern, repeated mistake, or missing constraint:
- If repo-universal (applies to all contributors): update this file in the same PR
- If session-specific (debugging notes, personal workflow): write to agent memory, not here
