import { getAuthHeaders } from "@/lib/auth/session";

/**
 * Phase 1 API origin (browser → FastAPI on port 8000).
 * Supports NEXT_PUBLIC_API_URL and NEXT_PUBLIC_API_BASE_URL.
 * Empty env values fall back to localhost:8000 (never relative /auth/token on :3000).
 */
function resolveApiBaseUrl(): string {
  const raw =
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (raw) {
    return raw.replace(/\/$/, "");
  }
  return "http://localhost:8000";
}

const BASE_URL = resolveApiBaseUrl();

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function normalizeErrorMessage(
  status: number,
  body: unknown
): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "detail" in body
  ) {
    const detail = (body as { detail: unknown }).detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "object" &&
          item !== null &&
          "msg" in item
            ? String((item as { msg: unknown }).msg)
            : String(item)
        )
        .join(", ");
    }
  }

  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body
  ) {
    return String((body as { error: unknown }).error);
  }

  if (status === 404) {
    return `API not found at ${BASE_URL} — is Phase 1 backend running? (uvicorn backend.phase1.app:app)`;
  }

  return `Request failed (${status})`;
}

function mergeRequestHeaders(options: RequestInit): Record<string, string> {
  const merged: Record<string, string> = {
    ...getAuthHeaders(),
  };

  const extra = options.headers;
  if (!extra) {
    return merged;
  }

  if (extra instanceof Headers) {
    extra.forEach((value, key) => {
      merged[key] = value;
    });
    return merged;
  }

  if (Array.isArray(extra)) {
    for (const [key, value] of extra) {
      merged[key] = value;
    }
    return merged;
  }

  Object.assign(merged, extra);
  return merged;
}

function buildRequestHeaders(options: RequestInit): Record<string, string> {
  const headers = mergeRequestHeaders(options);
  const hasContentType = Object.keys(headers).some(
    (key) => key.toLowerCase() === "content-type",
  );
  if (options.body !== undefined && !hasContentType) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

function buildRequestUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE_URL}${normalized}`;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = buildRequestUrl(path);
  const headers = buildRequestHeaders(options);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let body: unknown;

    try {
      body = await response.json();
    } catch {
      body = undefined;
    }

    throw new ApiError(
      normalizeErrorMessage(response.status, body),
      response.status,
      body
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export { BASE_URL, resolveApiBaseUrl };
