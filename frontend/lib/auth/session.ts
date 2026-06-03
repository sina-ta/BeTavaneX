const AUTH_TOKEN_KEY = "auth_token";
const AUTH_ROLE_KEY = "auth_role";
const AUTH_USERNAME_KEY = "auth_username";
const AUTH_SESSION_KEY = "isLoggedIn";

// The token is mirrored into a cookie so Next.js middleware (which cannot read
// localStorage) can enforce route protection. Not HttpOnly — it is written by
// client JS for dev/integration; harden to an HttpOnly cookie in production.
const TOKEN_COOKIE = "auth_token";
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 8;

function setCookie(name: string, value: string, maxAgeSeconds: number): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${name}=${encodeURIComponent(
    value
  )}; path=/; max-age=${maxAgeSeconds}; SameSite=Lax`;
}

function deleteCookie(name: string): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${name}=; path=/; max-age=0; SameSite=Lax`;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(AUTH_TOKEN_KEY, token);
  setCookie(TOKEN_COOKIE, token, COOKIE_MAX_AGE_SECONDS);
}

export function clearAuthToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(AUTH_TOKEN_KEY);
  deleteCookie(TOKEN_COOKIE);
}

export function getAuthRole(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_ROLE_KEY);
}

export function setAuthRole(role: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(AUTH_ROLE_KEY, role);
}

export function getAuthUsername(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_USERNAME_KEY);
}

export function setAuthUsername(username: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(AUTH_USERNAME_KEY, username);
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return Boolean(getAuthToken());
}

export function setSessionActive(active: boolean): void {
  if (active) {
    localStorage.setItem(AUTH_SESSION_KEY, "true");
    return;
  }

  localStorage.removeItem(AUTH_SESSION_KEY);
}

export function clearSession(): void {
  clearAuthToken();
  setSessionActive(false);

  if (typeof window !== "undefined") {
    localStorage.removeItem(AUTH_ROLE_KEY);
    localStorage.removeItem(AUTH_USERNAME_KEY);
  }
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}
