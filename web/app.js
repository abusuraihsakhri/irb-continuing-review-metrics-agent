"use strict";

/**
 * Browser-only reproduction of the three deterministic rules in agents/workers.py.
 * This is an illustrative assessment, not a validated IRB or clinical decision tool.
 */
function assess(input) {
  const text = (value, label, max) => {
    if (typeof value !== "string" || !value.trim() || value.trim().length > max) {
      throw new Error(label + " must contain 1–" + max + " characters.");
    }
    return value.trim();
  };
  const metric = (value, label) => {
    if (value === null || value === undefined || String(value).trim() === "") {
      throw new Error(label + " is required.");
    }
    const number = Number(value);
    if (!Number.isFinite(number)) {
      throw new Error(label + " must be a finite number.");
    }
    return number;
  };

  const taskId = text(input.task_id, "Task ID", 128);
  const targetId = text(input.target_identifier, "Target identifier", 128);
  const descriptor = text(input.status_descriptor ?? "NOMINAL", "Status descriptor", 64);
  const primary = metric(input.primary_metric, "Primary metric");
  const secondary = metric(input.secondary_metric ?? 0, "Secondary metric");
  const critical = input.is_critical_flag === true;
  const alerts = [];

  if (primary > 25) {
    alerts.push({
      origin_worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Primary Metric Threshold Exceeded",
      technical_details: "Primary measurement (" + primary.toFixed(2) + ") exceeds demonstration threshold 25.00.",
      actionable_remediation: "Review the source measurement and the configured threshold."
    });
  }
  if (critical || secondary > 12) {
    alerts.push({
      origin_worker: "SafetyEscalationWorker",
      urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Critical Safety Interlock Triggered",
      technical_details: "CriticalFlag=" + critical + " with secondary index " + secondary.toFixed(2) + ".",
      actionable_remediation: "Review the flagged record with an authorized supervisor."
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
      .some(flag => descriptor.toUpperCase().includes(flag))) {
    alerts.push({
      origin_worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Protocol Conformance Discordance Detected",
      technical_details: "Descriptor '" + descriptor + "' matched a configured anomaly keyword.",
      actionable_remediation: "Review the descriptor and its originating record."
    });
  }

  const overall = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC")
    ? "CRITICAL_STAT_PANIC"
    : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    mode: "LOCAL_RULE_DEMONSTRATION",
    task_id: taskId,
    target_identifier: targetId,
    overall_urgency: overall,
    integrity_status: overall === "CRITICAL_STAT_PANIC" ? "RECALIBRATION_REQUIRED"
      : overall === "ELEVATED_RISK" ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length,
    alerts
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { assess };
}

if (typeof document !== "undefined") {
  let evaluated = 0;
  let latestResult = null;
  const form = document.getElementById("assessment-form");
  const output = document.getElementById("result");
  const error = document.getElementById("form-error");
  const download = document.getElementById("download");

  form.addEventListener("submit", event => {
    event.preventDefault();
    error.textContent = "";
    try {
      const data = new FormData(form);
      latestResult = assess({
        task_id: data.get("task_id"),
        target_identifier: data.get("target_identifier"),
        primary_metric: data.get("primary_metric"),
        secondary_metric: data.get("secondary_metric"),
        status_descriptor: data.get("status_descriptor"),
        is_critical_flag: data.has("is_critical_flag")
      });
      evaluated++;
      document.getElementById("total").textContent = String(evaluated);
      document.getElementById("alerts").textContent = String(latestResult.total_alerts);
      const status = document.getElementById("status");
      status.textContent = latestResult.overall_urgency;
      status.dataset.level = latestResult.overall_urgency;
      output.textContent = JSON.stringify(latestResult, null, 2);
      download.disabled = false;
    } catch (exception) {
      latestResult = null;
      download.disabled = true;
      output.textContent = "No assessment available. Correct the form and run again.";
      error.textContent = exception.message;
    }
  });

  download.addEventListener("click", () => {
    if (!latestResult) return;
    const blob = new Blob([JSON.stringify(latestResult, null, 2) + "\n"], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "irb-assessment-demo.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  });
}
