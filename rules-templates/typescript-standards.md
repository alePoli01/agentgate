# TypeScript Standards

## Idiomatic Patterns
- Enable `strict: true` in tsconfig.json.
- Use `interface` for object shapes, `type` for unions/intersections.
- Prefer `readonly` for immutable state.
- Use discriminated unions for modeling state variants.
- Use explicit return types on exported functions.

## Anti-Patterns
- Never use `any`. Use `unknown` if the type is truly not known.
- Avoid non-null assertions (`!`) unless logically guaranteed.
- Do not use enums (prefer string literal unions or `as const` objects).
- Avoid default exports (use named exports).

## Example: Good vs Bad Code
**Bad Code**:
```typescript
let data: any;
function getUser(id: number) {
    if (id) return { id, name: "Test" };
    return null;
}
```

**Good Code**:
```typescript
type User = { readonly id: number; readonly name: string };

function getUser(id: number): User | null {
    if (id <= 0) return null;
    return { id, name: "Test" };
}
```

## Tool Recommendations
- Linter: `eslint` with `@typescript-eslint`
- Formatter: `prettier`

## Project Structure & Modularity (core-rules §11)
Organize code strictly by responsibility layer. Never mix UI components, state management, and network calls:
- components/: UI components (strictly one component per file).
- hooks/: Custom state management and lifecycle hooks.
- pi/ or services/: Fetch wrappers and API clients.
- 	ypes/: Type definitions and interfaces.
- utils/: Pure utility functions and formatters.

**Rules**:
- Keep files under ~300 lines and components/functions under ~50 lines.
- Extract sub-components, modals, and list items into dedicated files rather than nesting them in large views.
