/**
 * Phase 1 authentication — OAuth2 password flow against `POST /auth/token`.
 *
 * Reuses the shared `apiRequest` HTTP client (no second client). The token
 * endpoint expects form-encoded credentials; the JWT carries `sub` and `role`
 * claims which are decoded client-side and persisted via the auth session.
 */

import { apiRequest } from "@/lib/api/client";
import {
  clearSession,
  setAuthRole,
  setAuthToken,
  setAuthUsername,
  setSessionActive,
} from "@/lib/auth/session";
import type { AuthSession, TokenResponse } from "./types";

interface JwtClaims {
  sub?: string;
  role?: string;
  exp?: number;
  [key: string]: unknown;
}

/** Decode a JWT payload segment (no signature verification — display only). */
export function decodeJwtClaims(token: string): JwtClaims | null {
  const segments = token.split(".");
  if (segments.length !== 3) {
    return null;
  }

  try {
    const base64 = segments[1].replace(/-/g, "+").replace(/_/g, "/");
    const padding = (4 - (base64.length % 4)) % 4;
    const padded = base64.padEnd(base64.length + padding, "=");
    const json =
      typeof atob === "function"
        ? atob(padded)
        : Buffer.from(padded, "base64").toString("binary");
    return JSON.parse(json) as JwtClaims;
  } catch {
    return null;
  }
}

/** Request an access token using the OAuth2 password grant. */
export async function requestAccessToken(
  username: string,
  password: string
): Promise<TokenResponse> {
  const body = new URLSearchParams({
    username,
    password,
  }).toString();

  return apiRequest<TokenResponse>("/auth/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
}

/**
 * Authenticate and persist the session (token + role + username).
 * Returns the resolved session for the caller to use (e.g. redirect).
 */
export async function signIn(
  username: string,
  password: string
): Promise<AuthSession> {
  const { access_token } = await requestAccessToken(username, password);

  const claims = decodeJwtClaims(access_token);
  const role = (claims?.role as string | undefined) ?? "";
  const resolvedUsername =
    (claims?.sub as string | undefined) ?? username;

  setAuthToken(access_token);
  setAuthRole(role);
  setAuthUsername(resolvedUsername);
  setSessionActive(true);

  return {
    accessToken: access_token,
    role,
    username: resolvedUsername,
  };
}

/** Clear all persisted auth state. */
export function signOut(): void {
  clearSession();
}
