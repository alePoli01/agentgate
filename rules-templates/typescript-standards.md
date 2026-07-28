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
