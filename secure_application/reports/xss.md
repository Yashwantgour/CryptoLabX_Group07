# Cross-Site Scripting (XSS)

## Vulnerability

XSS in the Student Portal search/profile rendering path.

## Root Cause

The intentionally vulnerable laboratory version renders untrusted
input without appropriate HTML output encoding.

## Impact

Attacker-controlled JavaScript may execute in a victim's browser
when the vulnerable response is rendered.

## Evidence

Run the local XSS test and capture the browser behavior in the
isolated laboratory environment.

## Recommended Mitigation

Use the template engine's normal escaping behavior and do not mark
untrusted content as safe HTML.
