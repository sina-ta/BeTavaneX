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
    <section className="section-card">
      <section className="flex items-start gap-4">
        <section className="text-2xl">⚡</section>

        <section>
          <section className="mb-2 flex items-center gap-3">
            <span className="text-2xl font-bold text-white">
              {title}
            </span>

            {recommendation?.severity && (
              <SeverityBadge
                severity={recommendation.severity}
              />
            )}
          </section>

          <section className="text-lg text-gray-400">
            {message}
          </section>

          {recommendation?.explanation && (
            <section className="mt-2 text-sm text-gray-500">
              {recommendation.explanation}
            </section>
          )}
        </section>
      </section>
    </section>
  );
}
