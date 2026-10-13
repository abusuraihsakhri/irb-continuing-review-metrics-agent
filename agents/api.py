"""
FastAPI REST API Server for Irb Continuing Review Metrics Agent.
"""
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from .base import AuditLogger, SecurityException
from .metrics import GLOBAL_METRICS
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Irb Continuing Review Metrics Agent API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "irb-continuing-review-metrics-agent", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    started = time.perf_counter()
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        GLOBAL_METRICS.record_phi_block()
        raise HTTPException(status_code=422, detail="Input contains a prohibited identifier")
    GLOBAL_METRICS.record_task(dossier.overall_urgency.value, time.perf_counter() - started)
    return dossier.to_dict()


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def prometheus_metrics():
    return GLOBAL_METRICS.export_prometheus_text()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        GLOBAL_METRICS.record_phi_block()
        raise HTTPException(status_code=422, detail="Input contains a prohibited identifier")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
