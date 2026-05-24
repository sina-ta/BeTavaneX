import {
  resolveSeverity,
  type SeverityLevel,
} from "@/lib/operational/severity";

export type OperationalMetric = {
  progress: number;
  severity: SeverityLevel;
};

export function cpiToOperationalHealth(
  cpi: number
): OperationalMetric {
  const progress = Math.min(
    Math.max(cpi * 100, 0),
    100
  );

  if (cpi >= 1) {
    return { progress, severity: "healthy" };
  }

  if (cpi >= 0.85) {
    return { progress, severity: "warning" };
  }

  return { progress, severity: "critical" };
}

export function spiToOperationalHealth(
  spi: number
): OperationalMetric {
  const progress = Math.min(
    Math.max(spi * 100, 0),
    100
  );

  if (spi >= 0.95) {
    return { progress, severity: "healthy" };
  }

  if (spi >= 0.8) {
    return { progress, severity: "warning" };
  }

  return { progress, severity: "critical" };
}

export function ratioToOperationalHealth(
  numerator: number,
  denominator: number
): OperationalMetric {
  if (denominator <= 0) {
    return { progress: 0, severity: "warning" };
  }

  const ratio = numerator / denominator;
  const progress = Math.min(ratio * 100, 100);

  if (ratio >= 0.8) {
    return { progress, severity: "healthy" };
  }

  if (ratio >= 0.5) {
    return { progress, severity: "warning" };
  }

  return { progress, severity: "critical" };
}

export function alertToSeverity(
  alert: string
): SeverityLevel {
  return resolveSeverity(alert);
}
