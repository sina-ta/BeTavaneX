export interface ValidationFinding {
  rule_id: string;
  target: string;
  severity: string;
  passed: boolean;
  message: string;
  explanation: string;
  confidence: number;
  affected_entities?: Record<string, unknown>;
  operational_impact?: string;
}

export interface OperationalAnomaly {
  id: number;
  entity_type: string;
  entity_id: number;
  anomaly_type: string;
  severity: string;
  confidence?: number | null;
  explanation?: string | null;
  operational_impact?: string | null;
}

export interface ValidationPipelineResult {
  trusted: boolean;
  status: string;
  trust_score: number;
  validation_score: number;
  consistency_score: number;
  findings: ValidationFinding[];
  anomalies: Array<Record<string, unknown>>;
  warnings: string[];
  summary: string;
}

export interface ValidationSummary {
  total_validated: number;
  trusted_count: number;
  active_anomalies: number;
}

export interface ReportValidation {
  report_id: number;
  trust_score: number;
  validation_score: number;
  consistency_score: number;
  status: string;
  summary?: string | null;
}
