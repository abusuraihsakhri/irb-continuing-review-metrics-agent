# Irb Continuing Review Metrics Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Standards:** CAP / CLSI / ISO | HHS 45 CFR 46 / FDA 21 CFR 56 (IRB Rules)

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Irb Continuing Review Metrics Agent is a multi-agent evaluation platform that processes clinical and biomedical metrics through specialized worker agents. It classifies results by urgency (ROUTINE, ELEVATED, CRITICAL), enforces Zero-PHI outbound guards, and maintains a tamper-evident HMAC-SHA256 audit trail for every evaluation.

The system provides two coordinated evaluation pipelines:
- **`agents/`** — Core distributed component workers (InvariantQC, SafetyEscalation, ProtocolConformance) with a FastAPI REST server and Prometheus telemetry.
- **`irb_compliance/`** — IRB compliance sub-agents (EnrollmentVelocity, AdverseEventRate, ProtocolAmendmentAuditor) evaluating human-subject protection protocols.

---

## ⚙️ Key Capabilities

- **Multi-Agent Evaluation**: Three specialized workers assess each task payload and produce a consensus dossier.
- **Risk & Urgency Classification**: ROUTINE / ELEVATED_RISK / CRITICAL_STAT_PANIC tiers with automated remediation recommendations.
- **Zero-PHI Outbound Guard**: Regex-based detection and blocking of SSNs, MRNs, phone numbers, emails, and patient identifiers.
- **Tamper-Evident Audit Trail**: Chained HMAC-SHA256 signed logs for every evaluation and state transition.
- **FastAPI REST & Prometheus Telemetry**: Exposes `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs` endpoints.
- **Active Learning Calibration**: Bayesian weight tracking for worker reliability and Brier calibration drift.

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/irb-continuing-review-metrics-agent.git
cd irb-continuing-review-metrics-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set required environment variable for audit trail
export AUDIT_SECRET_KEY=$(openssl rand -hex 32)
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### CLI Parameter Reference
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--task-id` | Unique task / case identifier | `TASK-2026-001` |
| `--target` | Entity or specimen target identifier | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement (float) | `28.5` |
| `--secondary` | Secondary metric (float) | `14.2` |
| `--critical` | Trigger emergency escalation flag | `False` |
| `--status` | Status/phenotype descriptor | `DISCORDANT` |

### Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task / case identifier | Required |
| `target_identifier` | string | Entity, patient key, or target | Required |
| `primary_metric` | float | Primary domain measurement | Required |
| `secondary_metric` | float | Secondary metric (default 0.0) | Optional |
| `is_critical_flag` | boolean | Emergency escalation trigger | Optional |
| `status_descriptor` | string | Status code or phenotype | Optional |

---

## 🛡️ Security & Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB, and patient names.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs. Requires `AUDIT_SECRET_KEY` environment variable.
* **Input Validation:** Pydantic models enforce string length limits and reject NaN/Inf metric values.
* **Air-Gapped LLM Adapter:** Deterministic mock by default; supports Ollama, Claude, and OpenAI via `LLMFactory`.
* **FastAPI & Prometheus Telemetry:** Operational metrics and REST endpoints for integration.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build

# Or manually with Docker
docker build -t irb-continuing-review-metrics-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=$(openssl rand -hex 32) irb-continuing-review-metrics-agent
```

---

## 📁 Project Structure

```
irb-continuing-review-metrics-agent/
├── agents/                  # Core multi-agent evaluation pipeline
│   ├── api.py               # FastAPI REST server
│   ├── base.py              # PHI guard, HMAC audit trail, security
│   ├── models.py            # Pydantic data models
│   ├── supervisor.py        # Master orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── metrics.py           # Prometheus telemetry collector
│   ├── llm_factory.py       # LLM provider abstraction
│   ├── learning.py          # Bayesian calibration engine
│   └── streamer.py          # WebSocket telemetry broadcaster
├── irb_compliance/          # IRB compliance evaluation pipeline
│   ├── agents.py            # Compliance sub-agents
│   ├── engine.py            # Domain evaluation engine
│   ├── models.py            # Compliance data models
│   ├── server.py            # Compliance FastAPI server
│   └── cli.py               # Compliance CLI entry point
├── tests/                   # Pytest test suite
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulation
├── enrichment.py            # Domain enrichment engines
├── web/index.html           # Operations console UI
├── Dockerfile               # Container build
├── docker-compose.yml       # Multi-service orchestration
└── pyproject.toml           # Project metadata and dependencies
```
