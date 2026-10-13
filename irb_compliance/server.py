"""
FastAPI REST API Server for IRB-Compliance: Institutional Review Board Protocol Safety Metric Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import IRBComplianceCoordinator

coordinator = IRBComplianceCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="IRB-Compliance: Institutional Review Board Protocol Safety Metric Agent",
            description="Calculates subject enrollment velocity, adverse event incident rates, protocol amendment logs, and unapproved deviations.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = Field(default="TASK-2026-001", min_length=1, max_length=128)
            target_identifier: str = Field(default="TARGET-BIO-KEY", min_length=1, max_length=128)
            primary_metric: float = Field(default=28.5, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.2, allow_inf_nan=False)
            status_descriptor: str = Field(default="DISCORDANT_ANOMALY", min_length=1, max_length=64)
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "irb-continuing-review-metrics-agent", "domain": "Human Subject Protection", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
