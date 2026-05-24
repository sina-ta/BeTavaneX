const AUTH_TOKEN_KEY = "auth_token";
const AUTH_SESSION_KEY = "isLoggedIn";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return (
    Boolean(getAuthToken()) ||
    localStorage.getItem(AUTH_SESSION_KEY) === "true"
  );
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
