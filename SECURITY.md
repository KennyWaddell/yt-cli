# Security Policy

## Supported Versions

Security fixes and updates are provided for the latest release and the `main` branch:

| Version | Supported |
| :--- | :---: |
| `v1.5.x` (`main`) | ✅ |
| `< v1.5` | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability in **YT-CLI**, please **do not** open a public GitHub Issue.

Instead, report it privately using **GitHub Private Vulnerability Reporting**:
1. Go to the [**Security**](https://github.com/KennyWaddell/yt-cli/security) tab of this repository.
2. Click **Report a vulnerability** (under *Security Advisories*).
3. Provide clear reproduction steps, affected component (`bin/yt-cli`, `windows/yt_cli_gui.py`, or CI scripts), and impact.

You will receive an initial response as soon as possible to coordinate a fix and responsible disclosure.

## Integrity Verification (Windows Portable)

All official Windows binaries (`YT-CLI-Windows-Portable.zip`) are compiled transparently on GitHub Actions from public source code. Before running the executable, verify its SHA-256 checksum against the `SHA256.txt` file attached to the same release:

```powershell
Get-FileHash .\YT-CLI-Windows-Portable.zip -Algorithm SHA256
```

## Credential & Cookie Handling

- **Zero credential storage:** YT-CLI does not extract, copy, or store browser session cookies in plaintext files. When `--cookies-from-browser` (or the GUI `Cookies` dropdown) is used, browser handling is delegated directly to `yt-dlp`.
- **Zero telemetry:** YT-CLI performs no background analytics, tracking, or external network requests outside user-initiated searches, playback, and downloads.
