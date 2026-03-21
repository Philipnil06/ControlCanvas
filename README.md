# ControlCanvas

ControlCanvas is a local research harness for evaluating AI-generated frontend code with a safety-inspection protocol.

It runs:
- an untrusted builder model that generates HTML/CSS/JS,
- an inspector model that flags suspicious behavior,
- a simulation layer that produces run traces, metrics, and paper-style findings.

## What This Project Does

- Generates realistic benign and adversarial frontend samples.
- Runs protocol evaluations across model pairs and prompt variants.
- Tracks valid vs excluded runs with explicit status taxonomy.
- Supports deep-dive inspection per run (raw output, parsed JSON, translation, ground truth).
- Exports data for analysis and paper-style reporting.

## Current Run Configuration

Simulation is currently fixed to:
- `gpt-5.4-mini -> gpt-4.1-mini`: 30 runs
- `gpt-5.4-mini -> gpt-5.4`: 10 runs
- `gpt-5.4-mini -> o4-mini`: 10 runs

Total cap: **50 runs**.

## Repository Structure

```text
.
|-- Frontend.Html       # Main UI
|-- index.html          # Redirect to Frontend.Html
|-- styles.css          # UI styling
|-- app.js              # Frontend logic, simulation, metrics, exports
|-- app.py              # Local HTTP server + /api/llm endpoint
|-- start_server.bat    # Windows helper to launch server
|-- .env.example        # Environment template
|-- .gitignore
`-- README.md
```

## Requirements

- Python 3.9+ (tested with Python 3.13)
- OpenAI API key
- Modern browser (Chrome/Edge/Firefox)

No external Python dependencies are required (stdlib-only server).

## Quick Start

1. Copy environment template:
```bash
cp .env.example .env
```
Windows PowerShell alternative:
```powershell
Copy-Item .env.example .env
```

2. Set your key in `.env`:
```env
OPENAI_API_KEY=sk-...
USE_FAKE_DATA=false
```

3. Start server:
```bash
python app.py
```

4. Open:
```text
http://127.0.0.1:8000/
```

Windows shortcut:
```bat
start_server.bat
```

## UI Workflow

1. Enter a prompt and click `Generate`.
2. Run `Inspect Code` to evaluate and sanitize output.
3. Use `Protocol Evaluation` to run full experiments.
4. Open `Deep Dive` for any run to inspect traces.

## Experiments

Available experiment modes:
- `main_eval`
- `inspector_ablation`
- `builder_ablation`
- `baseline_comparison`
- `robustness_repeat`

The UI also includes:
- baseline comparison table,
- inspector/builder ablations,
- model x attack-family cross tables,
- controlled-pair findings,
- mechanism-vs-necessity summaries.

## Attack Family Taxonomy

Main adversarial families:
- `storage`
- `interaction_capture`
- `timing`
- `event`
- `network`
- `ui_manipulation`

Benign control runs use:
- `none`

## Validity and Status Rules

Valid statuses:
- `VALID_BENIGN_PASS`
- `VALID_TRUE_POSITIVE`
- `VALID_FALSE_NEGATIVE`
- `VALID_FALSE_POSITIVE`
- `VALID_TRUE_NEGATIVE`

Excluded statuses:
- `BUILDER_FORMAT_ERROR`
- `INSPECTOR_FORMAT_ERROR`
- `REQUEST_ERROR`
- `TIMEOUT_ERROR`
- `RUN_ERROR`
- `PARSE_ERROR`
- `INVALID_GROUND_TRUTH`
- `INVALID_EVAL_RECORD`

By default, official metrics are computed on `VALID_*` runs.

## Exports

- `Export Run Traces`: full trace list
- `Export Filtered Runs`: only active filtered subset
- `Export Research Pack`: aggregated research JSON
- `Export Paper Files`: paper-facing summary bundle

Typical key export:
- `full_runs.json`

## API Endpoints

- `POST /api/llm`
  - Modes: `builder`, `safe_builder`, `inspector`, `sim_builder`, `sim_inspector`
- `GET /api/methodology`
  - Returns experiment/methodology metadata used for reporting.

## Troubleshooting

- `Missing OPENAI_API_KEY`
  - Ensure `.env` exists and contains `OPENAI_API_KEY=...`.
- Simulation stops mid-run
  - Usually model/API timeout or parse failure; inspect `final_status` and deep-dive data.
- Stale UI behavior
  - Server sends no-cache headers; do a hard refresh if needed.

## Notes for GitHub

- `.env` is ignored by git.
- Use `.env.example` for collaborators.
- Keep exported run files out of commits unless they are intentional artifacts.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
