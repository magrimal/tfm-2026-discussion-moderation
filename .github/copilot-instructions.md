---
description: 'Python/Django code review instructions for GitHub Copilot'
applyTo: '**/*.py'
excludeAgent: ["coding-agent"]
---

# Code Review Instructions

Comprehensive code review guidelines for Python/Django projects using GitHub Copilot.

## Review Language

When performing a code review, respond in **English**.

## Review Priorities

When performing a code review, prioritize issues in the following order:

### 🔴 CRITICAL (Block merge)

- **Security**: Vulnerabilities, exposed secrets, authentication/authorization issues
- **Correctness**: Logic errors, data corruption risks, race conditions
- **Breaking Changes**: API contract changes without versioning
- **Data Loss**: Risk of data loss or corruption

### 🟡 IMPORTANT (Requires discussion)

- **Code Quality**: Violations of SOLID principles, excessive duplication
- **Test Coverage**: Missing tests for critical paths or new functionality
- **Performance**: N+1 queries, memory leaks, missing pagination
- **Architecture**: Deviations from established patterns

### 🟢 SUGGESTION (Non-blocking)

- **Readability**: Poor naming, complex logic that could be simplified
- **Optimization**: Performance improvements without functional impact
- **Best Practices**: Minor deviations from conventions
- **Documentation**: Missing or incomplete docstrings

## General Review Principles

1. **Be specific**: Reference exact lines and provide concrete examples
2. **Provide context**: Explain WHY something is an issue
3. **Suggest solutions**: Show corrected code, not just what's wrong
4. **Be constructive**: Focus on improving the code
5. **Recognize good practices**: Acknowledge well-written code
6. **Be pragmatic**: Not every suggestion needs immediate implementation

## Linting & Formatting

- Code must pass **ruff** (replaces isort, pycodestyle, flake8, black)
- Imports must follow ruff's isort rules (`I` rule set)
- Maximum line length: 80 characters

## Comments

- Reject in-line comments that describe **what** the code does
- Accept comments only when they explain **why**
- Flag redundant comments that restate obvious logic
- Docstrings are acceptable for public APIs and complex functions

### Examples

```python
# ❌ BAD: Describes what
x = x + 1  # increment x by 1

# ✅ GOOD: Explains why
x = x + 1  # compensate for zero-based indexing in external API
```

## Design Principles

- **Simple over complex**: flag overly complicated solutions
- **Explicit over implicit**: flag magic or hidden behavior
- **Flat over nested**: flag deep nesting (max 3 levels), suggest early returns
- **YAGNI**: flag features not yet needed
- **DRY**: flag repetition, but also flag premature abstractions
- **Single responsibility**: functions should do one thing, under 30 lines

### Examples

```python
# ❌ BAD: Deep nesting
def process(user):
    if user:
        if user.is_active:
            if user.has_permission('write'):
                return do_work()
    return None

# ✅ GOOD: Early returns
def process(user):
    if not user or not user.is_active:
        return None
    if not user.has_permission('write'):
        return None
    return do_work()
```

## Error Handling

- Flag empty `except` blocks (swallowed exceptions)
- Flag overly broad `except Exception` without re-raising
- Flag missing error context in re-raised exceptions
- Flag silent failures - errors must be logged or propagated

### Examples

```python
# ❌ BAD: Silent failure
def process_user(user_id):
    try:
        user = db.get(user_id)
        user.process()
    except:
        pass

# ✅ GOOD: Explicit error handling
def process_user(user_id):
    if not user_id or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    try:
        user = db.get(user_id)
    except UserNotFoundError:
        raise UserNotFoundError(f"User {user_id} not found")
    except DatabaseError as e:
        raise ProcessingError(f"Failed to retrieve user {user_id}") from e

    return user.process()
```

## Database & Transactions

- Verify **ACID** compliance when data integrity is critical
- Flag long-running transactions - keep them short
- Ensure proper rollback handling on errors
- Flag raw SQL without parameterized queries
- Flag N+1 query patterns - use `select_related`/`prefetch_related`
- Flag missing pagination on large querysets

### Examples

```python
# ❌ BAD: N+1 query
users = User.objects.all()
for user in users:
    orders = Order.objects.filter(user_id=user.id)  # N+1!

# ✅ GOOD: Eager loading
users = User.objects.prefetch_related('orders').all()
for user in users:
    orders = user.orders.all()
```

## Django Patterns

- Flag Django models or querysets exposed in public APIs - use data classes
- Flag business logic in signal handlers - keep handlers thin
- Flag circular imports - use `AppConfig.ready()` for signal registration
- Flag mixed REST and Python API code - keep them separate
- Verify versioned REST APIs in `rest_api/v1/`, `rest_api/v2/` structure

## Python Best Practices

- Flag missing type hints on function signatures
- Flag `os.path` usage - prefer `pathlib.Path`
- Flag resource handling without context managers (`with`)
- Flag `dataclasses` or `pydantic` misuse for structured data
- Flag generic `Exception` - require specific exception types
- Flag `print` statements - require `logging` module
- Flag magic numbers/strings - require named constants

### Examples

```python
# ❌ BAD: Magic numbers
def calculate_discount(total, price):
    if total > 100:
        return price * 0.15
    return price * 0.10

# ✅ GOOD: Named constants
PREMIUM_THRESHOLD = 100
PREMIUM_DISCOUNT_RATE = 0.15
STANDARD_DISCOUNT_RATE = 0.10

def calculate_discount(total: float, price: float) -> float:
    is_premium = total > PREMIUM_THRESHOLD
    rate = PREMIUM_DISCOUNT_RATE if is_premium else STANDARD_DISCOUNT_RATE
    return price * rate
```

## Async & Concurrency

- Flag blocking calls in async code
- Flag missing `await` keywords
- Flag potential race conditions
- Flag shared mutable state without locks

## Security

- Flag hardcoded secrets or credentials
- Flag unvalidated user input at system boundaries
- Flag potential injection vulnerabilities (SQL, command, XSS)
- Flag sensitive data in logs (passwords, tokens, PII)
- Flag missing authentication/authorization checks

### Examples

```python
# ❌ BAD: SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ GOOD: Parameterized query
User.objects.filter(email=email)
# or with raw SQL:
cursor.execute("SELECT * FROM users WHERE email = %s", [email])
```

```python
# ❌ BAD: Hardcoded secret
API_KEY = "sk_live_abc123xyz789"

# ✅ GOOD: Environment variable
import os
API_KEY = os.environ.get("API_KEY")
```

## Testing

- Flag tests without clear Arrange-Act-Assert structure
- Flag mocking of internal logic instead of external dependencies
- Flag missing edge case coverage
- Flag non-descriptive test names
- Use `pytest` as the test framework

### Examples

```python
# ❌ BAD: Vague name and assertion
def test1():
    result = calc(5, 10)
    assert result

# ✅ GOOD: Descriptive name and specific assertion
def test_calculate_discount_returns_10_percent_for_orders_under_100():
    order_total = 50
    item_price = 20

    discount = calculate_discount(order_total, item_price)

    assert discount == 2.00
```

## Code Organization

- Flag circular imports
- Flag god classes or functions doing too much
- Flag violation of separation of concerns
- Flag unused imports, variables, or functions
- Flag commented-out code blocks

## API Design

- Flag inconsistent response formats
- Flag breaking changes without versioning
- Flag missing error responses or status codes

## Dependencies

- Flag unpinned dependency versions
- Flag unnecessary dependencies when stdlib suffices

## Comment Format Template

When flagging issues, use this format:

```markdown
**[🔴/🟡/🟢] Category: Brief title**

Description of the issue.

**Why this matters:**
Impact or reason.

**Suggested fix:**
[code example]
```

## Review Checklist

### Code Quality

- [ ] Follows consistent style (ruff passes)
- [ ] Names are descriptive
- [ ] Functions are small and focused (< 30 lines)
- [ ] No code duplication
- [ ] Error handling is appropriate
- [ ] No commented-out code

### Security

- [ ] No secrets in code or logs
- [ ] Input validation on user inputs
- [ ] No SQL injection vulnerabilities
- [ ] Auth/authz properly implemented

### Testing

- [ ] New code has test coverage
- [ ] Tests are well-named and focused
- [ ] Tests cover edge cases
- [ ] Tests are independent

### Performance

- [ ] No N+1 queries
- [ ] Proper pagination
- [ ] Efficient algorithms

### Architecture

- [ ] Follows established patterns
- [ ] Proper separation of concerns
- [ ] Dependencies flow correctly

## Project Context

- **Tech Stack**: Python 3.x, Django, FastAPI, PostgreSQL
- **Linting**: ruff
- **Testing**: pytest
- **Code Style**: PEP 8 via ruff
