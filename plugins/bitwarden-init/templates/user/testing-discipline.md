## Testing Discipline

**Test behavior, not implementation. A good test fails for one reason — a real bug.**

- Default to the cheapest layer that observes the behavior — unit → handler with doubles → integration → E2E. Only move up when you can name what you'd see that you can't see lower.
- Mock setup is a boundary smell — if setup exceeds the assertion, change the boundary.
- Assert on outputs and side effects, not on which internals were called.
- One behavior per test. Split unrelated assertions into separate tests.
- Don't test pure glue (dependency injection, config binding, generated code) or code that only fails when the framework breaks.
- Test a "trivial" default only when a silent future change could break behavior that depends on it.
