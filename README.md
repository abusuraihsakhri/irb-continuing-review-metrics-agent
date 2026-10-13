# IRB Continuing Review Metrics Agent

A Python rule-evaluation demonstration with two independent pipelines, a REST API, command-line interfaces, and a browser-only rule demo. The repository does **not** implement a validated IRB continuing-review decision model: its numeric thresholds and keyword rules are illustrative, not thresholds established by 45 CFR 46 or 21 CFR 56.

## Capabilities

- **Core pipeline (`agents/`)**: classifies a primary metric above 25, a secondary metric above 12, a critical flag, and anomaly keywords into routine, elevated, or critical alert tiers.
- **Compliance-named pipeline (`irb_compliance/`)**: separate example engine with primary threshold 25 and secondary threshold 10. It does not calculate actual enrollment rates, adverse event incidence, or regulatory compliance.
- **HMAC audit chain**: the core Python pipeline signs in-memory records with a required environment key and verifies both signatures and predecessor links. The chain is not a persistent, externally anchored audit archive.
- **Input safeguards**: model validation rejects invalid or nonfinite metrics; heuristic checks reject certain obvious identifier patterns. These are not full PHI detection or HIPAA de-identification.
- **Browser demo (`web/`)**: self-contained, no-backend JavaScript assessment with JSON export. The browser demo does not generate HMAC audit records.

## Browser use

Open `web/index.html` directly in a modern desktop or mobile browser to try the local demonstration. No Python installation, Pyodide, CDN, server, or API keys are required. The JavaScript reproduces the **core** pipeline's three decision rules, not the compliance-named pipeline.

GitHub Pages deployment is configured in `.github/workflows/pages.yml`. The repository owner must enable **Settings → Pages → Build and deployment → GitHub Actions** before the initial deployment; a live URL should only be published here once verified.

**Privacy:** the static demo does not transmit or persist input data; entered values remain in tab memory unless exported as JSON. Do not enter patient-identifiable or other confidential data. The Python API and CLI may retain identifiers in process memory and audit metadata; use only synthetic or appropriately de-identified inputs.

## Python installation

Requires Python 3.9+ (CI tests 3.10–3.12).

```bash
python -m pip install -e ".[server]"
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
python cli.py audit --task-id DEMO-1 --target SYNTHETIC-1 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The core API serves `GET /health`, `GET /metrics` (JSON counters), `GET /metrics/prometheus` (Prometheus text), `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. Local OpenAPI documentation is at `http://127.0.0.1:8000/docs`. The `/api/chat` mock is deterministic and does not make LLM calls.

The installed `irb-continuing-review-metrics-engine` command, `python irb_compliance_app.py`, and `python -m irb_compliance.cli` use the **separate** compliance-named example pipeline. Use `python cli.py` for the core pipeline documented above.

## Test

```bash
python -m pip install -e ".[server,test]"
export AUDIT_SECRET_KEY="local-test-only-key"
python -m pytest -q
node --check web/app.js
node --test tests/web.test.cjs
```

## Docker

```bash
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

The compose service binds to `127.0.0.1:8000` by default. No audit secret is shipped in the container. Do not publicly expose the API without independent authentication, access controls, persistence design, and a privacy/security assessment.

## Project structure

- `agents/`: core input schemas, rule workers, supervisor, signed audit records, and FastAPI app
- `irb_compliance/`: alternate deterministic evaluation pipeline and CLI
- `web/`: browser-only rule demo, runnable as static files
- `tests/`: Python and JavaScript regression tests
- `cli.py`, `simulator.py`, `enrichment.py`: standalone command-line and example evaluation utilities

## License

[MIT](LICENSE). The software is not a medical device, IRB determination system, or substitute for institutional review, and is not certified against the cited regulations.
