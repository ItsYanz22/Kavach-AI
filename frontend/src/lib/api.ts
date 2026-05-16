/**
 * Kavach AI – Production-Grade API Discovery
 * 
 * LOGIC:
 * 1. If VITE_BACKEND_URL env var is set, use it (highest priority)
 * 2. If in development (Vite dev server), connect to localhost:8000
 * 3. If in production, use window.location.origin (same domain/protocol)
 * 4. Fallback: use window.location.origin
 * 
 * This ensures:
 * - Local development: http://localhost:8000
 * - Docker: http://backend:8000 (when VITE_BACKEND_URL=http://backend:8000)
 * - Cloud Run: https://app-id.run.app (same origin, no port)
 * - Localhost production: http://localhost:8080
 */

const isDev = import.meta.env.DEV;

function getApiBase(): string {
  // Priority 1: Environment variable (for custom backend URLs)
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl) {
    console.info(`[API] Using VITE_BACKEND_URL: ${envUrl}`);
    return envUrl;
  }

  // Priority 2: Development mode - connect to backend dev server
  if (isDev) {
    const devUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
    console.info(`[API] Dev mode → ${devUrl}`);
    return devUrl;
  }

  // Priority 3: Production - use same origin (frontend and backend same domain)
  const prodUrl = window.location.origin;
  console.info(`[API] Production mode → ${prodUrl}`);
  return prodUrl;
}

const API_BASE = getApiBase();

export function getBackendUrl() {
  return API_BASE;
}

export function getWsUrl() {
  // Determine WebSocket protocol based on current page protocol
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  
  // Determine host
  let wsHost: string;
  
  if (isDev) {
    // Development: connect to backend:8000
    wsHost = `${window.location.hostname}:8000`;
  } else if (import.meta.env.VITE_BACKEND_URL) {
    // Custom backend URL: parse host from it
    try {
      const url = new URL(import.meta.env.VITE_BACKEND_URL);
      wsHost = url.host; // includes port if present
    } catch {
      wsHost = window.location.host; // fallback
    }
  } else {
    // Production: same host as frontend
    wsHost = window.location.host;
  }
  
  const wsUrl = `${wsProtocol}//${wsHost}/ws/war-room`;
  console.info(`[WebSocket] ${wsUrl}`);
  return wsUrl;
}

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

export interface ActionStep {
  icon: string;
  text: string;
  detail: string;
}

export interface ActionResult {
  actions: ActionStep[];
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

/**
 * Production-grade API fetch wrapper with comprehensive error handling
 */
async function apiFetch<T>(
  path: string, 
  options?: RequestInit
): Promise<ApiEnvelope<T>> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = { 
    "Content-Type": "application/json" 
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  
  try {
    console.debug(`[FETCH] ${options?.method || 'GET'} ${url}`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
    
    const res = await fetch(url, {
      headers,
      ...options,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    // Log response status for debugging
    console.debug(`[FETCH] Response: ${res.status} ${res.statusText}`);
    
    if (!res.ok) {
      // Try to parse error body
      let errorDetail = `API error ${res.status}`;
      try {
        const errorBody = await res.json();
        errorDetail = errorBody?.detail || errorBody?.message || errorDetail;
      } catch {
        // Couldn't parse JSON, use status text
        errorDetail = res.statusText || errorDetail;
      }
      
      console.error(`[API ERROR] ${res.status}: ${errorDetail}`);
      throw new Error(errorDetail);
    }

    // Parse response
    const data = await res.json();
    console.debug(`[FETCH] Success: ${path}`);
    return data;
    
  } catch (error) {
    // Network errors, timeouts, etc.
    if (error instanceof TypeError) {
      // Common "Failed to Fetch" error
      console.error(`[NETWORK ERROR] Failed to fetch ${url}`);
      console.error(`  Possible causes:`);
      console.error(`  1. Backend is not running or unreachable`);
      console.error(`  2. CORS issue - check browser console`);
      console.error(`  3. Network connectivity problem`);
      console.error(`  4. Wrong API_BASE URL: ${API_BASE}`);
      throw new Error(
        `Network error: Cannot reach ${API_BASE}. Is the backend running? ` +
        `Check console for CORS errors.`
      );
    }
    
    if (error instanceof Error && error.name === 'AbortError') {
      console.error(`[TIMEOUT] Request to ${url} timed out after 30s`);
      throw new Error('Request timeout - backend is slow or unresponsive');
    }
    
    // Re-throw other errors
    throw error;
  }
}

// ── Endpoint helpers ───────────────────────────
export async function detectScam(text: string) {
  return apiFetch<DetectResult>("/api/detect", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function explainMessage(text: string) {
  return apiFetch<ExplainResult>("/api/explain", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function recommendAction(text: string) {
  return apiFetch<ActionResult>("/api/action", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function simulateScam() {
  return apiFetch<SimulateResult>("/api/simulate", {
    method: "POST",
  });
}

export async function fetchHistory() {
  return apiFetch<HistoryResult>("/api/history");
}

export async function fetchLearningModules() {
  return apiFetch<any[]>("/api/learning/modules");
}

export async function getDashboardData() {
  return apiFetch<any>("/api/learning/dashboard");
}
