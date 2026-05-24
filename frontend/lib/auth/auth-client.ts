export type UserRole = "admin" | "manager" | "engineer" | "viewer";

export type AuthUser = {
  id: string;
  email: string;
  roles: UserRole[];
};

export type LoginCredentials = {
  email: string;
  password: string;
};

export type AuthTokens = {
  accessToken: string;
  refreshToken?: string;
};

/**
 * Placeholder login — replace with real API call when auth is implemented.
 */
export async function login(
  credentials: LoginCredentials
): Promise<AuthTokens> {
  _validateCredentials(credentials);

  return {
    accessToken: "",
  };
}

export async function refreshAccessToken(): Promise<AuthTokens> {
  return {
    accessToken: "",
  };
}

export async function logout(): Promise<void> {
  return;
}

function _validateCredentials(
  credentials: LoginCredentials
): void {
  if (!credentials.email || !credentials.password) {
    throw new Error("Email and password are required");
  }
}
