"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { assess } = require("../web/app.js");
const base = { task_id: "T", target_identifier: "K", primary_metric: 10,
  secondary_metric: 3, status_descriptor: "NOMINAL", is_critical_flag: false };
test("routine rules", () => {
  const r = assess(base);
  assert.equal(r.overall_urgency, "ROUTINE");
  assert.equal(r.total_alerts, 0);
});
test("primary above threshold raises elevated alert", () => {
  const r = assess({ ...base, primary_metric: 25.01 });
  assert.equal(r.overall_urgency, "ELEVATED_RISK");
  assert.equal(r.alerts[0].origin_worker, "InvariantQCWorker");
});
test("secondary above threshold raises elevated alert", () => {
  assert.equal(assess({ ...base, secondary_metric: 12.1 }).overall_urgency, "ELEVATED_RISK");
});
test("critical flag overrides elevation", () => {
  const r = assess({ ...base, primary_metric: 30, is_critical_flag: true });
  assert.equal(r.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(r.critical_alerts_count, 1);
});
test("descriptor flags trigger conformance alert", () => {
  assert.equal(assess({ ...base, status_descriptor: "review_FAIL" }).total_alerts, 1);
});
test("threshold equality does not trigger alerts", () => {
  assert.equal(assess({ ...base, primary_metric: 25, secondary_metric: 12 }).total_alerts, 0);
});
test("invalid or blank values cannot produce a dossier", () => {
  assert.throws(() => assess({ ...base, task_id: "  " }));
  assert.throws(() => assess({ ...base, primary_metric: "NaN" }));
  assert.throws(() => assess({ ...base, primary_metric: "" }));
  assert.throws(() => assess({ ...base, secondary_metric: Infinity }));
});
