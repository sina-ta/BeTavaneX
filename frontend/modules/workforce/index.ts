export const WORKFORCE_EXTENSION_ENABLED =
  process.env.NEXT_PUBLIC_ENABLE_WORKFORCE_EXTENSION ===
  "true";

export {
  getWorkforceWorkers,
  getWorkforceWorkerById,
  getWorkerIntelligence,
  getWorkforceAnalytics,
  getWorkforceCrews,
  getWorkerEligibility,
} from "@/lib/api/workforce";

export type {
  WorkforceWorker,
  WorkforceWorkerDetail,
  WorkforceCrew,
  WorkforceAnalytics,
  WorkerIntelligence,
  WorkerScores,
  EligibilitySummary,
} from "@/types/workforce";
