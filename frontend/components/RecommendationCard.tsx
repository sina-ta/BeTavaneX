import SeverityBadge from "@/components/ui/SeverityBadge";
import type { Recommendation } from "@/types/common";

type Props = {
  title: string;
  message: string;
  recommendation?: Recommendation;
};

export default function RecommendationCard({
  title,
  message,
  recommendation,
}: Props) {
  return (
    <section className="ai-insight-panel">
      <div className="ai-insight-badge">AI Operational Insight</div>

      <section className="flex items-start gap-3">
        <section className="text-base">⚡</section>

        <section>
          <section className="mb-1 flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-white">
              {title}
            </span>

            {recommendation?.severity && (
              <SeverityBadge
                severity={recommendation.severity}
              />
            )}
          </section>

          <section className="text-sm text-gray-300 leading-snug">
            {message}
          </section>

          {recommendation?.explanation && (
            <section className="mt-2 text-xs text-gray-500">
              {recommendation.explanation}
            </section>
          )}
        </section>
      </section>
    </section>
  );
}
