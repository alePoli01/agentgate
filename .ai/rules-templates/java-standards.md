# Java Standards

## Idiomatic Patterns
- Use `Optional` for return types that can be null.
- Use modern Java features (Records, Streams, `var` where obvious).
- Favor composition over inheritance.
- Use dependency injection for testability.

## Anti-Patterns
- Avoid returning `null` — use `Optional`.
- Do not swallow exceptions (empty catch blocks).
- Avoid deep inheritance hierarchies.

## Example: Good vs Bad Code
**Bad Code**:
```java
public User findUser(String id) {
    if (id == null) return null;
    return database.get(id);
}
```

**Good Code**:
```java
public Optional<User> findUser(String id) {
    if (id == null || id.isBlank()) {
        return Optional.empty();
    }
    return Optional.ofNullable(database.get(id));
}
```

## Tool Recommendations
- Linter: `Checkstyle` or `SonarLint`
- Formatter: `Spotless`
