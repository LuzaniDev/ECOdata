const BASE = "";

let _apiKey = "";
let _keyPromise: Promise<string> | undefined;

async function loadApiKey(): Promise<string> {
  if (_apiKey) return _apiKey;
  if (!_keyPromise) {
    _keyPromise = fetch(`${BASE}/api/public/api-key`)
      .then((r) => r.json())
      .then((data: { api_key?: string }) => {
        _apiKey = data.api_key || "";
        return _apiKey;
      })
      .catch(() => {
        _apiKey = "";
        return _apiKey;
      });
  }
  return _keyPromise;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined | null>;
}

export async function api<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const key = await loadApiKey();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (key) {
    headers["Authorization"] = `Bearer ${key}`;
  }

  let url = `${BASE}${path}`;
  if (options.params) {
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(options.params)) {
      if (v !== undefined && v !== null && v !== "") {
        sp.set(k, String(v));
      }
    }
    const qs = sp.toString();
    if (qs) url += `?${qs}`;
  }

  const resp = await fetch(url, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `Erro ${resp.status}`);
  }

  return resp.json();
}

export function apiGet<T>(path: string, params?: Record<string, unknown>) {
  return api<T>(path, { params: params as Record<string, string | number | boolean | undefined | null> });
}

export function apiPost<T>(path: string, body?: unknown) {
  return api<T>(path, { method: "POST", body });
}

export function apiPut<T>(path: string, body?: unknown) {
  return api<T>(path, { method: "PUT", body });
}

export function apiDelete<T>(path: string, params?: Record<string, unknown>) {
  return api<T>(path, { method: "DELETE", params: params as Record<string, string | number | boolean | undefined | null> });
}

export async function downloadFile(path: string, filename?: string) {
  const key = await loadApiKey();
  const headers: Record<string, string> = {};
  if (key) {
    headers["Authorization"] = `Bearer ${key}`;
  }
  const resp = await fetch(`${BASE}${path}`, { headers });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `Erro ${resp.status}`);
  }
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || path.split("/").pop() || "download";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
