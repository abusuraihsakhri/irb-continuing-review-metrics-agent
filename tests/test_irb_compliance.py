import os
import sys
from pathlib import Path

# Set required environment variable before importing project modules
os.environ.setdefault("AUDIT_SECRET_KEY", "test-secret-key-for-pytest-2026")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from irb_compliance.models import FrontierPayload, ExecutionStatus
from irb_compliance.engine import FrontierDomainEngine
from irb_compliance.agents import EnrollmentVelocityAgent, AdverseEventRateCalculatorAgent, ProtocolAmendmentAuditorAgent, IRBComplianceCoordinator
from irb_compliance.cli import main


def test_sub_agents():
    a1 = EnrollmentVelocityAgent()
    p1 = FrontierPayload("T1", "KEY-01", primary_metric=35.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts1 = a1.audit(p1)
    assert len(alerts1) == 1
    assert alerts1[0].status == ExecutionStatus.ELEVATED_RISK

    a2 = AdverseEventRateCalculatorAgent()
    p2 = FrontierPayload("T2", "KEY-02", primary_metric=10.0, secondary_metric=15.0, status_descriptor="NOMINAL", is_critical_flag=True)
    alerts2 = a2.audit(p2)
    assert len(alerts2) == 1
    assert alerts2[0].status == ExecutionStatus.CRITICAL_INTERVENTION

    a3 = ProtocolAmendmentAuditorAgent()
    p3 = FrontierPayload("T3", "KEY-03", primary_metric=10.0, secondary_metric=4.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = a3.audit(p3)
    assert len(alerts3) == 1


def test_coordinator():
    coord = IRBComplianceCoordinator()
    p_nominal = FrontierPayload("T4", "KEY-04", primary_metric=12.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    dossier = coord.process(p_nominal)
    assert dossier["overall_status"] == ExecutionStatus.NOMINAL.value
    assert dossier["total_alerts"] == 0

    ans = coord.query_supervisory_chat("What standard is applied?")
    assert "HHS 45 CFR 46 / FDA 21 CFR 56 (IRB Rules)" in ans or "specifications" in ans


def test_cli():
    assert main(["audit", "--task-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0
