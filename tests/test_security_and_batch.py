"""Regression coverage for cryptographic audit verification and CSV parsing."""
import csv
import os

import pytest

os.environ.setdefault("AUDIT_SECRET_KEY", "ci-test-only-key")

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.api import app
from fastapi.testclient import TestClient
from cli import main as main_cli, parse_csv_bool as parse_core_bool
from irb_compliance.cli import main as compliance_cli, parse_csv_bool as parse_compliance_bool


def test_hmac_verification_detects_modification():
    audit = AuditTrail("test-key")
    audit.log("tester", "test", "CREATED", {"status": "ok"})
    audit.log("tester", "test", "FOLLOWUP", {"count": 2})
    assert audit.verify_integrity()
    audit.logs[0]["event_type"] = "TAMPERED"
    assert not audit.verify_integrity()


def test_exported_audit_log_cannot_mutate_original():
    audit = AuditTrail("test-key")
    audit.log("tester", "test", "CREATED", {"status": "ok"})
    audit.get_trail()[0]["event_type"] = "TAMPERED"
    assert audit.verify_integrity()


def test_full_metadata_is_screened_for_obvious_identifiers():
    payload = SystemTaskPayload(
        task_id="TASK-1", target_identifier="TARGET-1", primary_metric=1,
        attributes={"contact": "test@example.com"},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


@pytest.mark.parametrize("value,expected", [
    ("False", False), ("0", False), ("No", False), ("", False),
    ("True", True), ("1", True), ("YES", True),
])
def test_batch_boolean_parser(value, expected):
    assert parse_core_bool(value) is expected
    assert parse_compliance_bool(value) is expected


def test_batch_boolean_parser_rejects_ambiguous():
    with pytest.raises(ValueError):
        parse_core_bool("perhaps")


@pytest.mark.parametrize("cli", [main_cli, compliance_cli])
def test_false_string_does_not_trigger_critical_flag(tmp_path, cli):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "B-1,KEY-1,1,1,False,NOMINAL\n",
        encoding="utf-8",
    )
    assert cli(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    assert row.get("overall_urgency", row.get("overall_status")) in ("ROUTINE", "NOMINAL_OPTIMAL")


def test_api_phi_rejection_and_prometheus_counters():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "TEST", "target_identifier": "KEY", "primary_metric": 5,
        "attributes": {"email": "name@example.com"},
    })
    assert response.status_code == 422
    result = client.get("/metrics/prometheus")
    assert result.status_code == 200
    assert "text/plain" in result.headers["content-type"]
    assert "phi_outbound_blocks_total" in result.text
