# SQL Injection

## Vulnerability

SQL Injection in the Student Portal login/query functionality.

## Root Cause

The intentionally vulnerable laboratory version constructs an SQL
statement using user-controlled input rather than parameterized
queries.

## Impact

An attacker may manipulate the SQL statement and affect database
query behavior.

## Evidence

Use the local test environment and record the resulting request,
response, and relevant code line in the final screenshots.

## Recommended Mitigation

Use parameterized SQL:

```python
connection.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,),
)
```

Never concatenate untrusted input into SQL statements.
