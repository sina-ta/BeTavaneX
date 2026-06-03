export {
  getAuthToken,
  setAuthToken,
  clearAuthToken,
  getAuthRole,
  setAuthRole,
  getAuthUsername,
  setAuthUsername,
  isAuthenticated,
  setSessionActive,
  clearSession,
  getAuthHeaders,
} from "./session";

export {
  login,
  logout,
  refreshAccessToken,
} from "./auth-client";

export type {
  UserRole,
  AuthUser,
  LoginCredentials,
  AuthTokens,
} from "./auth-client";

export {
  getPhase1Role,
  canPlan,
  canAssignWorkOrders,
  canApproveSteps,
  canSubmitDailyReports,
  isReadOnlyInvestor,
  canAccessOperationalConsole,
  canReadRuntime,
} from "./role-policy";
