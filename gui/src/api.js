const API_BASE = window.location.port === "1420" ? "http://127.0.0.1:14200" : "";

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/api/status`);
  return res.json();
}

export async function fetchEntries(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/api/entries?${query}`);
  return res.json();
}

export async function createEntry(entry) {
  const res = await fetch(`${API_BASE}/api/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entry),
  });
  return res.json();
}

export async function deleteEntry(id) {
  const res = await fetch(`${API_BASE}/api/entries/${id}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  return res.json();
}

export async function fetchDistortions() {
  const res = await fetch(`${API_BASE}/api/distortions`);
  return res.json();
}

export async function fetchEmotions() {
  const res = await fetch(`${API_BASE}/api/emotions`);
  return res.json();
}

// Behavioral Experiments
export async function fetchExperiments() {
  const res = await fetch(`${API_BASE}/api/experiments`);
  return res.json();
}

export async function createExperiment(exp) {
  const res = await fetch(`${API_BASE}/api/experiments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(exp),
  });
  return res.json();
}

export async function completeExperiment(id, data) {
  const res = await fetch(`${API_BASE}/api/experiments/${id}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteExperiment(id) {
  const res = await fetch(`${API_BASE}/api/experiments/${id}`, {
    method: "DELETE",
  });
  return res.json();
}

// Anti-Procrastination Tasks
export async function fetchTasks() {
  const res = await fetch(`${API_BASE}/api/tasks`);
  return res.json();
}

export async function createTask(task) {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  return res.json();
}

export async function completeTask(id, data) {
  const res = await fetch(`${API_BASE}/api/tasks/${id}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteTask(id) {
  const res = await fetch(`${API_BASE}/api/tasks/${id}`, {
    method: "DELETE",
  });
  return res.json();
}

// Exposure Ladders & Desensitization
export async function fetchLadders() {
  const res = await fetch(`${API_BASE}/api/ladders`);
  return res.json();
}

export async function createLadder(data) {
  const res = await fetch(`${API_BASE}/api/ladders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function buildLadder(data) {
  const res = await fetch(`${API_BASE}/api/ladders/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function addLadderStep(ladderId, data) {
  const res = await fetch(`${API_BASE}/api/ladders/${ladderId}/steps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function practiceLadderStep(stepId, data) {
  const res = await fetch(`${API_BASE}/api/exposure-steps/${stepId}/practice`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteLadder(ladderId) {
  const res = await fetch(`${API_BASE}/api/ladders/${ladderId}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function deleteExposureStep(stepId) {
  const res = await fetch(`${API_BASE}/api/exposure-steps/${stepId}`, {
    method: "DELETE",
  });
  return res.json();
}

// Action Items
export async function fetchActions(isDone = null) {
  const url = isDone !== null ? `${API_BASE}/api/actions?is_done=${isDone}` : `${API_BASE}/api/actions`;
  const res = await fetch(url);
  return res.json();
}

export async function createAction(data) {
  const res = await fetch(`${API_BASE}/api/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function toggleAction(id, done) {
  const res = await fetch(`${API_BASE}/api/actions/${id}/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ done }),
  });
  return res.json();
}

export async function deleteAction(id) {
  const res = await fetch(`${API_BASE}/api/actions/${id}`, {
    method: "DELETE",
  });
  return res.json();
}

// Burns DAS Assessment
export async function fetchDasQuestions() {
  const res = await fetch(`${API_BASE}/api/das/questions`);
  return res.json();
}

export async function fetchDasHistory() {
  const res = await fetch(`${API_BASE}/api/das`);
  return res.json();
}

export async function submitDas(data) {
  const res = await fetch(`${API_BASE}/api/das`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// Burns 10 Techniques Catalog
export async function fetchMethods() {
  const res = await fetch(`${API_BASE}/api/methods`);
  return res.json();
}

// Clinical Audit / Verification
export async function fetchVerifyAudit() {
  const res = await fetch(`${API_BASE}/api/verify`);
  return res.json();
}

// Thought Quality Evaluation (David Burns' Refutation Checker)
export async function evaluateThought(data) {
  const res = await fetch(`${API_BASE}/api/evaluate-thought`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// Backup & Restore
export async function fetchBackup() {
  const res = await fetch(`${API_BASE}/api/backup`);
  return res.json();
}

export async function restoreBackup(data) {
  const res = await fetch(`${API_BASE}/api/restore`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function triggerSync() {
  const res = await fetch(`${API_BASE}/api/sync`, { method: "POST" });
  return res.json();
}
