# SAST Lab Report: Flawfinder

## Installation Log
- **Operating system and version**: macOS (Darwin)
- **SAST tool name and version**: Flawfinder version 2.0.20
- **Dependencies/prerequisites installed**: Python 3.9, pip
- **Installation procedure**: 
  ```bash
  python3 -m pip install flawfinder --user
  ```
- **Installation or configuration problems encountered**: Flawfinder was installed in a directory (`/Users/kunalsachan/Library/Python/3.9/bin`) that was not in the system's `PATH`.
- **How each problem was resolved**: Rather than modifying the system `PATH`, the tool was invoked using its absolute path (`/Users/kunalsachan/Library/Python/3.9/bin/flawfinder`).

## Program Creation
A small program `vulnerable.cpp` was created containing:
- Hard-coded credentials
- Unsafe command execution (`system()`)
- Unsafe C/C++ functions (`strcpy()`, `sprintf()`)
- Statically-sized arrays

## Findings (Sample)

### Finding 1: Buffer Overflow (strcpy)
- **Vulnerability/security issue detected**: Does not check for buffer overflows when copying to destination
- **File and line number**: `vulnerable.cpp:10`
- **Severity/confidence**: Level 4
- **Rule/check ID**: CWE-120 (MS-banned)
- **Explanation provided by the tool**: `strcpy` does not check for buffer overflows when copying to destination.
- **Suggested remediation**: Consider using `snprintf`, `strcpy_s`, or `strlcpy` (warning: `strncpy` easily misused).

### Finding 2: Buffer Overflow (sprintf)
- **Vulnerability/security issue detected**: Does not check for buffer overflows
- **File and line number**: `vulnerable.cpp:30`
- **Severity/confidence**: Level 4
- **Rule/check ID**: CWE-120
- **Explanation provided by the tool**: `sprintf` does not check for buffer overflows.
- **Suggested remediation**: Use `sprintf_s`, `snprintf`, or `vsnprintf`.

### Finding 3: Unsafe Command Execution
- **Vulnerability/security issue detected**: This causes a new program to execute and is difficult to use safely
- **File and line number**: `vulnerable.cpp:31`
- **Severity/confidence**: Level 4
- **Rule/check ID**: CWE-78
- **Explanation provided by the tool**: This causes a new program to execute and is difficult to use safely.
- **Suggested remediation**: Try using a library call that implements the same functionality if available.

### Finding 4: Statically-Sized Arrays
- **Vulnerability/security issue detected**: Statically-sized arrays can be improperly restricted, leading to potential overflows or other issues
- **File and line number**: `vulnerable.cpp:8` (also 21, 24, 29)
- **Severity/confidence**: Level 2
- **Rule/check ID**: CWE-119!/CWE-120
- **Explanation provided by the tool**: Statically-sized arrays can be improperly restricted, leading to potential overflows or other issues.
- **Suggested remediation**: Perform bounds checking, use functions that limit length, or ensure that the size is larger than the maximum possible length.

## Terminal Log
The terminal activity log has been saved in `sast_lab_log.txt` as per the lab instructions.
