# Rust Standards

## Idiomatic Patterns
- Use `Result` and `Option` extensively.
- Use the `?` operator for error propagation.
- Prefer borrowing (`&T`) over cloning.
- Group logic into `impl` blocks; use traits for shared behavior.
- Use `#[derive(...)]` for common trait implementations.

## Anti-Patterns
- Avoid `unwrap()` and `expect()` in production code.
- Don't use `unsafe` unless absolutely necessary and documented.
- Avoid monolithic functions; break into smaller testable units.

## Example: Good vs Bad Code
**Bad Code**:
```rust
fn parse_id(s: &str) -> u32 {
    s.parse::<u32>().unwrap()
}
```

**Good Code**:
```rust
use std::num::ParseIntError;

fn parse_id(s: &str) -> Result<u32, ParseIntError> {
    s.parse::<u32>()
}
```

## Tool Recommendations
- Linter: `clippy`
- Formatter: `rustfmt`
