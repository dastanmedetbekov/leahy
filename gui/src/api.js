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

export async function triggerSync() {
  const res = await fetch(`${API_BASE}/api/sync`, { method: "POST" });
  return res.json();
}
