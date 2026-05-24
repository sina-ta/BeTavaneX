import { apiRequest } from "./client";
import type { DashboardData } from "@/types/dashboard";

export function getDashboardData(): Promise<DashboardData> {
  return apiRequest<DashboardData>("/dashboard");
}
