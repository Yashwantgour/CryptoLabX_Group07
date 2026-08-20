# Security Test Cases

Group 7 Student Portal security tests.

## Tests

- `test_sqli.py` - login/query security tests
- `test_xss.py` - reflected XSS behavior
- `test_idor.py` - unauthorized profile access

## Run

From `secure_application/`:

```bash
pytest testcases -v
```

The tests are intended for the isolated local laboratory application.
