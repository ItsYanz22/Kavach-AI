/**
 * Kavach AI – Backend API client
 *
 * All backend calls go through this module so the base URL
 * is configured in exactly one place.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface DetectResult {
  classification: string;   // "SCAM" | "SAFE"
  confidence: number;       // 0 – 1
  reason: string;
}

export interface ExplainResult {
  message_parts: { text: string; highlight_index: number | null }[];
  highlights: { label: string; color: string; icon: string; tooltip: string; text: string }[];
  reasons: string[];
}

export interface ActionResult {
  actions: string;
}

export interface SimulateResult {
  message: string;
}

export interface HistoryEntry {
  id: number;
  message: string;
  classification: string;
  confidence: number;
  timestamp: string;
}

export interface HistoryResult {
  history: HistoryEntry[];
}

// ── Generic fetch wrapper ──────────────────────
async function apiFetch<T>(path: string, options?: RequestInit): Promise<ApiEnvelope<T>> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    throw new Error(errorBody?.detail ?? `API error ${res.status}`);
  }

  return res.json();
}

// ── Endpoint helpers ───────────────────────────
export async function detectScam(text: string) {
  return apiFetch<DetectResult>("/detect", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function explainMessage(text: string) {
  return apiFetch<ExplainResult>("/explain", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function recommendAction(text: string) {
  return apiFetch<ActionResult>("/action", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function simulateScam() {
  return apiFetch<SimulateResult>("/simulate", {
    method: "POST",
  });
}

export async function fetchHistory() {
  return apiFetch<HistoryResult>("/history");
}
