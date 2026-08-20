# Group 7 — Student Portal Security Assessment

## Group Members

- Member 1: __________________
- Member 2: __________________

## Project

Student Portal

## Core Functionality

- Login
- Course registration
- Grade viewing
- Profile updates

## Intentional Vulnerabilities

Exactly three:

1. SQL Injection
2. Cross-Site Scripting (XSS)
3. Insecure Direct Object Reference (IDOR)

## Testing

Automated tests are stored in `testcases/`.

Run:

```bash
pytest testcases -v
```

## SAST

Semgrep is used for static analysis.

```bash
semgrep scan --config auto src
```

## Evidence

Add final screenshots to `screenshots/` and reference them here.

## Findings

### SQL Injection

Describe the vulnerable query, evidence, impact, and parameterized-query mitigation.

### XSS

Describe the unsafe rendering, evidence, impact, and output-encoding mitigation.

### IDOR

Describe the missing authorization check, evidence, impact, and server-side authorization mitigation.

## Conclusion

The Student Portal was tested in an isolated local laboratory. The
three selected vulnerabilities were demonstrated and remediation
recommendations were documented.
