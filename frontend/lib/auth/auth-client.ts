/**
 * Auth facade — delegates to the Phase 1 OAuth2 password flow.
 *
 * Login fields historically used "email"; Phase 1 authenticates by username,
 * so the credential's identifier is forwarded as the username. Token + role
 * persistence is handled inside `signIn` (see lib/api/phase1/auth).
 */

import {
  signIn,
  signOut,
} from "@/lib/api/phase1/auth";
import { getAuthToken } from "@/lib/auth/session";

export type UserRole = "admin" | "supervisor" | "worker" | "investor";

export type AuthUser = {
  username: string;
  role: UserRole | string;
};

export type LoginCredentials = {
  /** Username (the login form labels this field generically). */
  email: string;
  password: string;
};

export type AuthTokens = {
  accessToken: string;
  refreshToken?: string;
};

export async function login(
  credentials: LoginCredentials
): Promise<AuthTokens> {
  _validateCredentials(credentials);

  const session = await signIn(credentials.email, credentials.password);

  return {
    accessToken: session.accessToken,
  };
}

/**
 * Phase 1 issues short-lived tokens and exposes no refresh endpoint, so this
 * returns the currently stored token. Re-login is required after expiry.
 */
export async function refreshAccessToken(): Promise<AuthTokens> {
  return {
    accessToken: getAuthToken() ?? "",
  };
}

export async function logout(): Promise<void> {
  signOut();
}

function _validateCredentials(
  credentials: LoginCredentials
): void {
  if (!credentials.email || !credentials.password) {
    throw new Error("Username and password are required");
  }
}
