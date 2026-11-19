# Command reference

Moved from the README. The quickstart in the [README](../README.md#quickstart) needs only `init`, `doctor`, `plan` and `run`.

## Commands

All commands can also be invoked with the installed `aptflow` entry point.

| Command | Purpose | External calls |
|---|---|---|
| `python aptflow.py --version` | Print the version without loading configuration | None |
| `python aptflow.py init [--config PATH]` | Create a demo config; refuses to overwrite it | None |
| `python aptflow.py doctor [--config PATH]` | Check adapters and required variable names | None |
| `python aptflow.py plan [--config PATH]` | Print explicit stage mapping and readiness | None |
| `python aptflow.py run --out PATH [--config PATH]` | Execute the configured mock workflow | None in this starter |
| `python aptflow.py render BUNDLE --out PATH [--font PATH]` | Render a local title-card MP4 | None |

Both `python aptflow.py --version` and the installed `aptflow --version` use the version declared in `aptflow_core/__init__.py`. The checkout does not require installed package metadata.

Exit codes: `0` for success; `1` for an execution/configuration error or failed `doctor` readiness; `2` for invalid CLI arguments. `plan` can return `0` while reporting `ready: false`: it inspects a configuration rather than executing it.

For a custom `init --config PATH`, its parent directory must already exist. Workflow output directories are created automatically and must not already exist.

## Optional CLI installation

In a virtual environment:

```console
python -m pip install -e .
aptflow --help
```

Running from a checkout requires no installation. Installation requires the build backend in `pyproject.toml`, which may be downloaded if absent.

Create an isolated environment first if desired:

```powershell
# Windows PowerShell; activation is optional.
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\aptflow.exe --help
```

```sh
# Linux/macOS
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/aptflow --help
```

## Optional video rendering

Install FFmpeg with drawtext/libx264, ffprobe and a TrueType font separately:

```console
python aptflow.py render outputs/my-first-run/storyboard.json --out outputs/my-first-video
```

Windows Arial, Linux DejaVu Sans and macOS Arial locations are tried as defaults. If none exists, pass `--font /path/to/font.ttf`. Rendering is silent title cards, entirely local. It writes `demo.mp4`, an input snapshot, source references, SHA-256 and a report checking duration, dimensions and full decoding. Source references are provenance; they do not automatically establish factual truth. Fonts and FFmpeg are not redistributed.

`examples/aptflow-demo.json` is a standalone synthetic fixture. Its example.com references are fictional, not live research.
