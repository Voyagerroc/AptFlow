# AptFlow

An account-independent starter for workflows that assign each task to a specialist tool.

**Clone, run the synthetic demo, then bring your own adapters and credentials.** No account, API key, Docker installation or network call is required for the default workflow.

## Implementation status

| Component | Status |
|---|---|
| Configuration, preflight and explicit workflow stages | Implemented |
| Account-free memory → research → script → storyboard demo | Implemented, synthetic data |
| Optional local FFmpeg rendering and media checks | Implemented |
| NotebookLM / TinyFish / model / HeyGen adapters | Extension stubs, not implemented |
| Activepieces workflow import | Not implemented; optional development container only |
| Canva / Descript | Future adapter ideas |

The mock video step produces a storyboard, not an avatar video. Selecting a provider or supplying credentials does not implement its adapter. No provider request is made by this starter.

## Quickstart

Requires Python 3.11+ and Git. Python's standard library is enough for the default demo. No cloud account, API key, FFmpeg or Docker is required for this quickstart.

```console
git clone https://github.com/Voyagerroc/AptFlow.git
cd AptFlow
python aptflow.py init
python aptflow.py doctor
python aptflow.py plan
python aptflow.py run --out outputs/my-first-run
```

Windows users can use `py -3.11`; some Unix systems use `python3` instead of `python`.

Expected result: the last command prints `status: demo_completed`, `synthetic: true`, `external_calls: 0` and `video_generated: false`. Inspect `outputs/my-first-run/storyboard.json` and `outputs/my-first-run/report.json`.

The last command writes `storyboard.json` and `report.json`. Every mock result is explicitly synthetic. Every run requires a fresh output directory and will not overwrite earlier work. The demo makes zero external calls.

`init` creates **your** ignored `aptflow.json`; it never overwrites an existing configuration. Change adapters and optional memory there. No personal notebook, account, source ID or machine path is included in the bundled demo.

### Optional CLI installation

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

## CLI reference

All commands can also be invoked with the installed `aptflow` entry point.

| Command | Purpose | External calls |
|---|---|---|
| `python aptflow.py init [--config PATH]` | Create a demo config; refuses to overwrite it | None |
| `python aptflow.py doctor [--config PATH]` | Check adapters and required variable names | None |
| `python aptflow.py plan [--config PATH]` | Print explicit stage mapping and readiness | None |
| `python aptflow.py run --out PATH [--config PATH]` | Execute the configured mock workflow | None in this starter |
| `python aptflow.py render BUNDLE --out PATH [--font PATH]` | Render a local title-card MP4 | None |

Exit codes: `0` for success; `1` for an execution/configuration error or failed `doctor` readiness; `2` for invalid CLI arguments. `plan` can return `0` while reporting `ready: false`: it inspects a configuration rather than executing it.

For a custom `init --config PATH`, its parent directory must already exist. Workflow output directories are created automatically and must not already exist.

## Optional video rendering

Install FFmpeg with drawtext/libx264, ffprobe and a TrueType font separately:

```console
python aptflow.py render outputs/my-first-run/storyboard.json --out outputs/my-first-video
```

Windows Arial, Linux DejaVu Sans and macOS Arial locations are tried as defaults. If none exists, pass `--font /path/to/font.ttf`. Rendering is silent title cards, entirely local. It writes `demo.mp4`, an input snapshot, source references, SHA-256 and a report checking duration, dimensions and full decoding. Source references are provenance; they do not automatically establish factual truth. Fonts and FFmpeg are not redistributed.

`examples/aptflow-demo.json` is a standalone synthetic fixture. Its example.com references are fictional, not live research.

## Configure your own tools

Edit your ignored `aptflow.json` or copy `config/live.example.json` to a private config path. The example maps optional memory to NotebookLM, research to TinyFish, planning to your chosen reasoning model, and avatar video to HeyGen.

Default configuration:

```json
{
  "schema_version": 1,
  "mode": "demo",
  "tools": {
    "memory": {"adapter": "mock", "enabled": true},
    "research": {"adapter": "mock", "enabled": true},
    "script": {"adapter": "mock", "enabled": true},
    "video": {"adapter": "mock", "enabled": true}
  }
}
```

Only memory can be disabled with `enabled: false`. Research, script and video are required. In demo mode every enabled stage must use `mock`. Unknown fields/adapters are rejected.

```console
python aptflow.py doctor --config config/live.example.json
python aptflow.py plan --config config/live.example.json
```

The live example intentionally fails readiness because provider adapters are **stubs**. It reports variable names and implementation state without printing credential values. A run with incomplete adapters fails preflight before creating outputs or making provider requests.

`.env.example` lists blank placeholders. **The CLI does not load .env automatically.** Set variables in your own shell or deployment platform. Do not commit credentials; .env, user config, outputs and local history are ignored.

| Live boundary | Environment variable names | Status |
|---|---|---|
| TinyFish | `TINYFISH_API_KEY` | Unimplemented |
| Your reasoning model | `MODEL_API_KEY`, `MODEL_NAME`, `MODEL_BASE_URL` | Unimplemented |
| HeyGen | `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` | Unimplemented |
| NotebookLM | `NOTEBOOKLM_NOTEBOOK_ID` plus your own authentication implementation | Unimplemented, optional |

These are proposed configuration names, not working connections. Inject credentials into the process environment for your future adapter; never put real values in a README, issue, pull request or committed JSON file.

See [adapter guide](docs/ADAPTERS.md). NotebookLM authentication is optional and user-managed; a notebook ID alone is not authentication. Do not copy someone else's sessions, private memories or credentials.

## Architecture

```text
Your config → preflight → memory (optional) → research → script → video/storyboard
                                                           → validation → local artifacts
```

This starter uses explicit role mapping, not autonomous tool selection. `workflows/product-promo.json` is a design specification, not an importable Activepieces flow.

## Optional Activepieces backend

Docker is optional and unrelated to the CLI demo. `compose.yaml` is a single-instance local prototype based on the vendor's [hobbyist guide](https://www.activepieces.com/docs/install/options/docker).

```console
docker compose config --quiet
docker compose up -d
```

Open http://localhost:8095 and create your own account. This embedded setup has migration limitations and is not for production. The image defaults to latest for evaluation; pin a tested digest before a reproducible release. Compose has not been validated on this machine.

## Development

```console
python -m unittest discover -s tests -v
```

A GitHub Actions template is provided for account-free tests and the demo on Windows/Linux; it is not active in this repository. Media rendering is optional. See [CONTRIBUTING.md](CONTRIBUTING.md).

### Enable GitHub Actions in your copy

The workflow template is [templates/github-actions/ci.yml](templates/github-actions/ci.yml). Copy it to `.github/workflows/ci.yml` in your own repository and commit it using an identity/token allowed to modify workflows. It tests Python 3.11 and 3.13 on Windows and Linux with no API credentials.

The initial publication's OAuth connection did not have GitHub's `workflow` permission. The template is therefore distributed as a normal file rather than falsely advertising active CI. Local tests passed; a passing GitHub Actions run is not claimed.

All examples are synthetic. No complete creative SaaS chain, automatic factual verification, cost savings or provider endorsement is claimed. The starter is MIT licensed; provider services and separately installed media tools have their own terms.

## Repository layout

```text
aptflow.py                 Direct CLI entry point
aptflow_core/
  cli.py                   init / doctor / plan / run / render
  config.py                Strict configuration validation
  adapters.py              Provider contracts, mock adapters, live stubs
  workflow.py              Stage execution and artifact report
  media.py                 Optional local video rendering
  demo-config.json         Account-free bundled config
config/live.example.json   Non-working live extension example
examples/                  Synthetic storyboard fixture
workflows/                 Future product-promo design specification
docs/ADAPTERS.md            Provider implementation guide
tests/                     Offline tests
templates/github-actions/  Optional CI workflow to enable in your own copy
compose.yaml               Optional Activepieces development container
.env.example               Empty credential reference, not auto-loaded
```

## Troubleshooting

| Symptom | What to do |
|---|---|
| Config file does not exist | Run `python aptflow.py init` first, or pass `--config PATH` |
| Config already exists | Edit it or initialize a different path; init will not replace it |
| Output directory already exists | Choose a new `--out` path; previous work is preserved |
| Live doctor reports not ready | Expected: implement/register the provider adapters before live use |
| An API key appears to have no effect | The starter does not implement live APIs or load .env automatically |
| FFmpeg/ffprobe is missing | Install both for render, or use the storyboard-only demo |
| Font is missing | Pass `--font` pointing to your own existing TrueType font |
| FFmpeg reports drawtext or libx264 missing | Use a build with those features; the core demo does not need FFmpeg |
| Video has no voice/avatar | Expected for local title-card rendering; no avatar service is called |

## Roadmap and contribution scope

- Implement one opt-in research adapter and add offline response fixtures.
- Add a model adapter with structured output and measurable usage.
- Implement asynchronous video job persistence/reconciliation and media delivery.
- Add appropriate live cost and status accounting; do not reuse mock report fields.
- Evaluate a real Activepieces export only after the chosen connections work.
- Add dynamic routing only with explicit capability rules and evaluation cases.

These are future tasks, not capabilities delivered by this version. A useful contribution is one documented adapter, its contract and failure tests. See [CONTRIBUTING.md](CONTRIBUTING.md) and [adapter guide](docs/ADAPTERS.md).

## Türkçe kısa başlangıç

Bu depo kişisel hesaptan bağımsız bir **geliştirme iskeletidir**. Varsayılan demo sentetik veri kullanır ve dış servise bağlanmaz. Yukarıdaki quickstart komutlarıyla başlayın; `aptflow.json` dosyanızı kendinize göre düzenleyin. Gerçek NotebookLM, TinyFish, model ve HeyGen adaptörleri henüz uygulanmamıştır: yalnızca API anahtarı girmek yeterli değildir. Docker ve FFmpeg varsayılan demo için gerekmez; video render için FFmpeg isteğe bağlıdır. Özel bilgiler ve çıktılar Git dışında tutulur.
