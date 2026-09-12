# fan-bracket-cad

Parametric [build123d](https://github.com/gumyr/build123d) model for 140mm
fan mounting brackets — 3 brackets, equally spaced across a 440x150mm case
cutout, each holding one 140mm fan (124.5mm hole spacing).

Parameters live at the top of `src/fan_bracket_cad/bracket.py` — edit and
re-run to regenerate the STEP files.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for environment and
dependency management. It's a single binary with the same commands on
Windows and Linux, so there's no venv-activation-script divergence to deal with.

### Install uv

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

(Or via pipx/pip on either OS: `pip install uv`.)

### Clone and sync

```bash
git clone <repo-url>
cd fan-bracket-cad
uv sync
```

`uv sync` reads `pyproject.toml` + `uv.lock`, creates `.venv/`, and installs
the exact locked dependency versions — identical on Windows and Linux.

### Build the model

```bash
uv run fan-bracket-build
```

This prints the derived dimensions and writes STEP files to `outputs/`:
- `fan_brackets_assembly.step` — all 3 brackets positioned across the opening
- `fan_bracket_single.step` — one bracket, for detail work / printing prep

### Import into your CAD viewer

Open the STEP files in FreeCAD, Fusion, or your viewer of choice. To check
fan-mount clearance against the real fan geometry, import Noctua's official
STEP model alongside it:
https://cdn.noctua.at/media/aebef570/NF-A14x25_G2_Public-CAD.zip

## Repo layout

```
fan-bracket-cad/
├── pyproject.toml          # dependencies + fan-bracket-build entry point
├── uv.lock                 # locked dependency versions (commit this)
├── src/fan_bracket_cad/
│   └── bracket.py          # all the parameters + geometry
├── outputs/                # generated STEP files (gitignored)
└── .github/workflows/
    └── ci.yml              # rebuilds the model on Linux + Windows on every push
```

## CI

`.github/workflows/ci.yml` runs `uv sync` + `uv run fan-bracket-build` on
both `ubuntu-latest` and `windows-latest` for every push, and uploads the
resulting STEP files as workflow artifacts. This catches any
platform-specific breakage (and any accidental syntax error) before it
reaches a print.
