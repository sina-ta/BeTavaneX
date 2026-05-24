"use client";

import { useState } from "react";

import SeverityBadge from "@/components/ui/SeverityBadge";
import type { Recommendation } from "@/types/common";

type TaskRecommendationCellProps = {
  recommendation?: Recommendation;
  alert: string;
};

export default function TaskRecommendationCell({
  recommendation,
  alert,
}: TaskRecommendationCellProps) {
  const [expanded, setExpanded] = useState(false);

  if (!recommendation) {
    return (
      <span className="text-sm text-gray-500">
        No recommendation
      </span>
    );
  }

  const severity =
    recommendation.severity ?? alert;

  return (
    <section className="task-recommendation-cell">
      <button
        type="button"
        className="task-recommendation-toggle"
        onClick={() => setExpanded((open) => !open)}
        aria-expanded={expanded}
      >
        <SeverityBadge severity={severity} />
        <span className="task-recommendation-title">
          {recommendation.title}
        </span>
        <span className="task-recommendation-expand">
          {expanded ? "−" : "+"}
        </span>
      </button>

      {expanded && (
        <section className="task-recommendation-detail">
          <p className="task-recommendation-action">
            {recommendation.action}
          </p>

          {recommendation.explanation && (
            <p className="task-recommendation-explanation">
              {recommendation.explanation}
            </p>
          )}

          {recommendation.factors &&
            recommendation.factors.length > 0 && (
              <ul className="task-recommendation-factors">
                {recommendation.factors.map((factor) => (
                  <li key={factor}>{factor}</li>
                ))}
              </ul>
            )}
        </section>
      )}
    </section>
  );
}
