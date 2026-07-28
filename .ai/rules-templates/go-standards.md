# Go Standards

## Idiomatic Patterns
- Return errors as the last return value.
- Use `fmt.Errorf("...: %w", err)` to wrap errors with context.
- Keep variable scope as small as possible.
- Use concise but descriptive names (`req` not `requestObject`).
- Accept interfaces, return structs.

## Anti-Patterns
- Do not use `panic` for normal error handling.
- Avoid large interfaces; prefer 1-2 method interfaces.
- Don't use `init()` unless strictly necessary.
- Never ignore errors with `_`.

## Example: Good vs Bad Code
**Bad Code**:
```go
func ReadFile(path string) (string, error) {
    bytes, err := os.ReadFile(path)
    if err != nil {
        return "", err  // no context
    }
    return string(bytes), nil
}
```

**Good Code**:
```go
func ReadFile(path string) (string, error) {
    b, err := os.ReadFile(path)
    if err != nil {
        return "", fmt.Errorf("reading file %q: %w", path, err)
    }
    return string(b), nil
}
```

## Tool Recommendations
- Linter: `golangci-lint`
- Formatter: `gofmt` or `goimports`
