import RecommendationCard from "@/components/RecommendationCard";
import type { Recommendation } from "@/types/common";

type RecommendationSectionProps = {
  recommendation?: Recommendation;
};

export default function RecommendationSection({
  recommendation,
}: RecommendationSectionProps) {
  if (!recommendation) {
    return null;
  }

  return (
    <RecommendationCard
      title={recommendation.title}
      message={recommendation.action}
      recommendation={recommendation}
    />
  );
}
