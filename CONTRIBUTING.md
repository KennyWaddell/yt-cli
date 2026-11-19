# Contributing to YT-CLI

Thank you for your interest in contributing to **YT-CLI**! This project is designed to stay fast, ultralight, and accessible on modest hardware (e.g., dual-core Intel Celeron / Atom systems and legacy PCs).

## Project Structure

- `bin/yt-cli`: Main Bash client for Linux terminals (`fzf` + `mpv` + `yt-dlp` + `ffmpeg`).
- `lang/*.sh`: Modular language packs for the Linux CLI (`en.sh` is the base fallback).
- `windows/yt_cli_gui.py`: Portable Tkinter GUI for Windows.
- `windows/locales_data.py`: Modular language dictionary for the Windows GUI (10 languages).
- `tests/`: Automated unit, syntax, and i18n parity tests.
- `.github/workflows/`: CI pipelines (`ci-tests.yml` on push/PR, `build-windows.yml` on release tags).

## Running Tests Locally

Before submitting a Pull Request, run the test suite from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

If you modify Bash scripts (`bin/yt-cli`, `install.sh`, `uninstall.sh`), also run `shellcheck`:

```bash
shellcheck -S error bin/yt-cli install.sh uninstall.sh
```

## Contributing Translations

1. **Linux CLI:** Copy `lang/en.sh` to `lang/<iso-code>.sh` (e.g. `lang/it.sh`), update `LANG_CODE` and `LANG_NAME`, and translate the `MSG_*` strings. `bin/yt-cli` discovers new packs automatically.
2. **Windows GUI:** Add your language tuple to `LANG_OPTIONS` and its dictionary to `GUI_STRINGS` in `windows/locales_data.py`.
3. Run `python3 -m unittest discover -s tests -v` to verify there are no missing keys or syntax errors.

## Security & Code Guidelines

- **No heavy dependencies:** Keep Linux CLI pure Bash and Windows GUI pure standard-library Tkinter.
- **Session cookies:** Never write browser cookies to custom plaintext files; always delegate to `yt-dlp`'s `--cookies-from-browser` (or user-provided paths).
- **Zero telemetry:** Never introduce analytics, external tracking, or background network calls unrelated to media playback/downloads.
