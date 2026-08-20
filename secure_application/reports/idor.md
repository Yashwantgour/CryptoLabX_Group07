# Insecure Direct Object Reference (IDOR)

## Vulnerability

IDOR in the Student Portal profile endpoint.

## Root Cause

The vulnerable endpoint accepts a profile identifier but does not
verify that the requested profile belongs to the authenticated user.

## Demonstration

Authenticate as Alice and request Alice's profile, then change the
identifier to Bob's profile identifier.

## Impact

An authenticated student may access another student's profile.

## Recommended Mitigation

Perform a server-side authorization check before returning the
resource. For example, require the requested user identifier to
match the authenticated user's identifier when students are only
allowed to access their own profile.
