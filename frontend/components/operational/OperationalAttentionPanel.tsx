"use client";

import { useCallback } from "react";
import Link from "next/link";

import { getProjectOperationalIntelligence } from "@/lib/api/phase1/intelligence";
import type { OperationalIntelligence } from "@/lib/api/phase1/intelligence";
import {
  canViewCoordinationDetail,
  canViewOperationalIntelligence,
  canViewSupervisorDecisionDetail,
  getPhase1Role,
} from "@/lib/auth/role-policy";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import CompactCard from "@/components/layout/primitives/CompactCard";

type Props = {
  projectId: string;
};

const BAND_STYLE: Record<string, string> = {
  GOOD: "#22c55e",
  ATTENTION: "#eab308",
  AT_RISK: "#ef4444",
  UNKNOWN: "var(--status-unknown)",
};

const COORD_BAND_STYLE: Record<string, string> = {
  ALIGNED: "#22c55e",
  FRAGMENTED: "#eab308",
  STRESSED: "#ef4444",
  UNKNOWN: "var(--status-unknown)",
};

export default function OperationalAttentionPanel({ projectId }: Props) {
  if (!canViewOperationalIntelligence()) {
    return null;
  }

  const fetchIntel = useCallback(
    () => getProjectOperationalIntelligence(projectId),
    [projectId],
  );
  const { status, data, error, reload } =
    useAsyncData<OperationalIntelligence>(fetchIntel);

  return (
    <CompactCard title="Operational attention">
      {status === "loading" && (
        <p className="page-subtitle">Analyzing runtime signals…</p>
      )}
      {status === "error" && (
        <p className="page-subtitle">
          Intelligence unavailable.{" "}
          <button type="button" className="button-ghost" onClick={reload}>
            Retry
          </button>
          {error && ` (${error})`}
        </p>
      )}
      {data && (
        <AttentionBody
          data={data}
          showSupervisorDetail={canViewSupervisorDecisionDetail()}
          showCoordinationDetail={canViewCoordinationDetail()}
        />
      )}
    </CompactCard>
  );
}

function AttentionBody({
  data,
  showSupervisorDetail,
  showCoordinationDetail,
}: {
  data: OperationalIntelligence;
  showSupervisorDetail: boolean;
  showCoordinationDetail: boolean;
}) {
  const bandColor = BAND_STYLE[data.health.band] ?? BAND_STYLE.UNKNOWN;
  const ds = data.decision_support;
  const ci = data.coordination_intelligence;
  const role = getPhase1Role();
  const isWorker = role === "worker";

  return (
    <div className="flex flex-col gap-4">
      <p className="page-subtitle">
        <span
          style={{
            color: bandColor,
            fontWeight: 600,
            marginInlineEnd: 8,
          }}
        >
          {data.health.band}
        </span>
        {data.health.score !== null && (
          <>
            Health score {data.health.score}/100 —{" "}
          </>
        )}
        {data.health.summary}
      </p>

      {!data.data_available && (
        <p className="page-subtitle">
          Connect PostgreSQL for full stagnation, approval, and blocker
          analysis.
        </p>
      )}

      {ci && isWorker && ci.worker_relevance.length > 0 && (
        <div>
          <strong className="text-emphasis">Your team coordination</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {ci.worker_relevance.map((line) => (
              <li key={line} className="planning-list-item page-subtitle">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      {ci && showCoordinationDetail && !isWorker && (
        <div>
          <p className="page-subtitle">
            <span
              style={{
                color:
                  COORD_BAND_STYLE[ci.coordination_band] ?? COORD_BAND_STYLE.UNKNOWN,
                fontWeight: 600,
                marginInlineEnd: 8,
              }}
            >
              Coordination {ci.coordination_band}
            </span>
            {ci.coordination_score !== null && (
              <> — score {ci.coordination_score}/100</>
            )}
            . {ci.coordination_summary}
          </p>
          {ci.team_execution_flow.reports_last_7_days !== undefined && (
            <p className="page-subtitle" style={{ fontSize: "0.9em" }}>
              Team flow (7d): {ci.team_execution_flow.reports_last_7_days} reports,{" "}
              {ci.team_execution_flow.approvals_last_7_days} approvals,{" "}
              {ci.team_execution_flow.open_coordination_dependencies} open dependencies
              (density {ci.team_execution_flow.coordination_density}).
            </p>
          )}
        </div>
      )}

      {ci && showCoordinationDetail && !isWorker && ci.coordination_attention.length > 0 && (
        <div>
          <strong className="text-emphasis">Coordination attention</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {(role === "investor"
              ? ci.coordination_attention.slice(0, 4)
              : ci.coordination_attention
            ).map((item) => (
              <li key={`${item.category}-${item.message}`} className="planning-list-item">
                <span
                  style={{
                    color:
                      item.severity === "critical"
                        ? "#ef4444"
                        : item.severity === "warning"
                          ? "#eab308"
                          : "var(--status-unknown)",
                  }}
                >
                  [{item.category}]
                </span>{" "}
                {item.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {ci &&
        showCoordinationDetail &&
        showSupervisorDetail &&
        ci.cross_role_dependencies.length > 0 && (
          <details>
            <summary className="compact-card__title" style={{ cursor: "pointer" }}>
              Cross-role dependencies ({ci.cross_role_dependencies.length})
            </summary>
            <ul className="planning-list">
              {ci.cross_role_dependencies.map((dep) => (
                <li key={dep.dependency_type} className="planning-list-item page-subtitle">
                  {dep.from_role} → {dep.to_role}: {dep.message}
                </li>
              ))}
            </ul>
          </details>
        )}

      {ci &&
        showCoordinationDetail &&
        showSupervisorDetail &&
        ci.handoff_risks.length > 0 && (
          <details>
            <summary className="compact-card__title" style={{ cursor: "pointer" }}>
              Handoff risks ({ci.handoff_risks.length})
            </summary>
            <ul className="planning-list">
              {ci.handoff_risks.map((h) => (
                <li key={`${h.handoff_type}-${h.message}`} className="planning-list-item page-subtitle">
                  {h.message}
                </li>
              ))}
            </ul>
          </details>
        )}

      {ds && ds.recommendations.length > 0 && !isWorker && (
        <div>
          <strong className="text-emphasis">What to do next</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {ds.recommendations.map((rec) => (
              <li
                key={rec.message}
                className="planning-list-item page-subtitle"
              >
                <span
                  style={{
                    color:
                      rec.severity === "critical"
                        ? "#ef4444"
                        : rec.severity === "warning"
                          ? "#eab308"
                          : "var(--status-unknown)",
                  }}
                >
                  [{rec.severity}]
                </span>{" "}
                {rec.message}
                <span style={{ display: "block", opacity: 0.85, marginTop: 4 }}>
                  {rec.rationale}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {ds && ds.supervisor_guidance.length > 0 && !isWorker && (
        <div>
          <strong className="text-emphasis">
            {showSupervisorDetail ? "Supervisor guidance" : "Operational summary"}
          </strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {(showSupervisorDetail
              ? ds.supervisor_guidance
              : ds.supervisor_guidance.slice(0, 3)
            ).map((line) => (
              <li key={line} className="planning-list-item page-subtitle">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      {ds && ds.priority_queue.length > 0 && !isWorker && (
        <div>
          <strong className="text-emphasis">Priority order (explainable)</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {(showSupervisorDetail ? ds.priority_queue : ds.priority_queue.slice(0, 5))
              .map((item) => (
                <li key={`${item.rank}-${item.title}`} className="planning-list-item">
                  <span style={{ color: "var(--status-unknown)", marginInlineEnd: 6 }}>
                    #{item.rank}
                  </span>
                  <strong>{item.title}</strong>
                  <span className="page-subtitle" style={{ display: "block" }}>
                    Score {item.priority_score} — {item.explanation}
                  </span>
                  {showSupervisorDetail && (
                    <span className="page-subtitle" style={{ display: "block" }}>
                      → {item.suggested_action}
                    </span>
                  )}
                </li>
              ))}
          </ul>
        </div>
      )}

      {showSupervisorDetail && ds && ds.approval_queue.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Approval queue ({ds.approval_queue.length})
          </summary>
          <ul className="planning-list">
            {ds.approval_queue.map((item) => (
              <li key={item.approval_id} className="planning-list-item page-subtitle">
                #{item.queue_position} {item.step_code} / {item.activity_code} —{" "}
                {item.days_pending}d pending
                {item.overdue ? " (overdue)" : ""}
              </li>
            ))}
          </ul>
        </details>
      )}

      {ds && ds.blocker_guidance.length > 0 && (
        <SignalGroup title="Blocker guidance" items={ds.blocker_guidance} />
      )}

      {showSupervisorDetail && ds && ds.workload_imbalance.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Workload imbalance
          </summary>
          <ul className="planning-list">
            {ds.workload_imbalance.map((w) => (
              <li key={w.imbalance_type} className="planning-list-item page-subtitle">
                {w.message}
              </li>
            ))}
          </ul>
        </details>
      )}

      {role === "investor" && ds && (
        <p className="page-subtitle" style={{ fontSize: "0.85em" }}>
          Investor view: priority risks and health only. Operational queues are
          supervisor-scoped.
        </p>
      )}

      {data.predictions.length > 0 && (
        <div>
          <strong className="text-emphasis">Forecasts (explainable)</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {data.predictions.map((item) => (
              <li key={`${item.forecast}-${item.reason}`} className="planning-list-item">
                <strong>{item.forecast}</strong> ({item.confidence}) — {item.reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.attention_needed.length > 0 ? (
        <ul className="planning-list">
          {data.attention_needed.map((item) => (
            <li key={`${item.category}-${item.message}`} className="planning-list-item">
              <span
                style={{
                  color:
                    item.severity === "critical"
                      ? "#ef4444"
                      : item.severity === "warning"
                        ? "#eab308"
                        : "var(--status-unknown)",
                }}
              >
                [{item.severity}]
              </span>{" "}
              {item.message}
              {item.workflow_step_id && (
                <>
                  {" "}
                  <Link
                    href={`/dashboard/activity-instances`}
                    className="text-link"
                    style={{ fontSize: "0.85em" }}
                  >
                    (review runtime)
                  </Link>
                </>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="page-subtitle">No urgent attention signals for this project.</p>
      )}

      {(data.stagnation.length > 0 ||
        data.approval_delays.length > 0 ||
        data.anomalies.length > 0) && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Signal detail
          </summary>
          <SignalGroup title="Stagnation" items={data.stagnation} />
          <SignalGroup title="Approval delays" items={data.approval_delays} />
          <SignalGroup title="Blockers" items={data.blocker_trends} />
          <SignalGroup title="Anomalies" items={data.anomalies} />
        </details>
      )}
    </div>
  );
}

function SignalGroup({
  title,
  items,
}: {
  title: string;
  items: OperationalIntelligence["stagnation"];
}) {
  if (items.length === 0) {
    return null;
  }
  return (
    <div style={{ marginTop: 12 }}>
      <strong className="text-emphasis" style={{ fontSize: "0.9em" }}>
        {title}
      </strong>
      <ul className="planning-list">
        {items.map((s) => (
          <li key={s.signal_type} className="planning-list-item page-subtitle">
            {s.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
