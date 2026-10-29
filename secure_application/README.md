# Secure Application: Student Portal (Group 07)

This directory contains the secure coding laboratory application for Group 07.

## Team Members
- Yashwant Gour (`2024ucp1732`)
- Kunal Sachan (`2024ucp1547`)

## Application Overview
A console-based Python application that simulates core Student Portal functionality while demonstrating three key security vulnerabilities:
1. **SQL Injection (SQLi)** in course search and authentication queries.
2. **Insecure Direct Object Reference (IDOR)** in student profile and grade viewing.
3. **Broken Access Control** in administrative grade-modification functions.

## Directory Structure
```
secure_application/
├── src/
│   ├── app.py              # Main terminal application logic
│   └── database.py         # SQLite database initialization & queries
├── sast/
│   ├── vulnerable.cpp      # SAST testing target (Flawfinder)
│   ├── sast_lab_log.txt    # Flawfinder execution log
│   └── README.md           # SAST report & remediation details
├── reports/                # Security assessment & testing reports
├── screenshots/            # Terminal session evidence
├── outputs/                # Execution outputs & logs
├── crypto/                 # Cryptographic routines
└── testcases/              # Security exploit payloads & test cases
```

## How to Run
```bash
python3 src/app.py
```
