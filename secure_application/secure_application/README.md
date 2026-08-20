# Group 7 — kunak Work

This archive contains the Mac-side security/testing/documentation
work for the Group 7 Student Portal.

## Ownership

Primary owner: kunal

- Security tests
- XSS testing documentation
- IDOR testing documentation
- SAST setup
- Reports
- Screenshot organization

The Windows teammate owns the core application files under `src/`.

## Important

Before pushing, pull the latest `student-portal` branch so these files
are merged with the teammate's current application.

## Recommended workflow

```bash
git checkout student-portal
git pull origin student-portal

# Copy/merge these files into secure_application/

git status
git add .gitignore testcases reports sast screenshots outputs README_mac_student.md
git commit -m "Add security tests SAST and assessment reports"
git pull --rebase origin student-portal
git push origin student-portal
```

Do not commit `.venv/`, local SQLite databases, or generated SAST JSON.
