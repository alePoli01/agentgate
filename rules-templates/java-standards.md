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

## Project Structure & Modularity (core-rules §11)
Organize packages by architectural layer:
- controller/: REST controllers and request mapping.
- service/: Business logic and transactional services.
- client/: External service clients and web client configs.
- model/ or dto/: Domain models and transfer objects.
- 
epository/: Persistence layer.

**Rules**:
- Keep files under ~300 lines and methods under ~50 lines.
- Exactly one top-level class or record per file.
