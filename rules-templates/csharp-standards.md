# C# Standards

## Idiomatic Patterns
- Enable Nullable Reference Types (`<Nullable>enable</Nullable>`).
- Use `async`/`await` for I/O bound operations.
- Prefer `IReadOnlyCollection` or `IEnumerable` for returning collections.
- Use records for immutable data types.

## Anti-Patterns
- Avoid `.Wait()` or `.Result` on tasks (deadlock risk).
- Do not catch `Exception` just to log and re-throw without `throw;`.
- Avoid public mutable fields.

## Example: Good vs Bad Code
**Bad Code**:
```csharp
public User GetUser(int id)
{
    var result = _db.Users.FindAsync(id).Result;
    return result;
}
```

**Good Code**:
```csharp
public async Task<User?> GetUserAsync(int id, CancellationToken ct = default)
{
    return await _db.Users.FindAsync(new object[] { id }, ct);
}
```

## Tool Recommendations
- Linter/Formatter: `dotnet format`, Roslyn analyzers
