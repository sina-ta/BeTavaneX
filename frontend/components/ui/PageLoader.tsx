import PageHeader from "./PageHeader";
import SectionCard from "./SectionCard";
import LoadingState from "./LoadingState";

type PageLoaderProps = {
  title: string;
  subtitle: string;
  message?: string;
};

export default function PageLoader({
  title,
  subtitle,
  message,
}: PageLoaderProps) {
  return (
    <div className="page-wrapper">
      <PageHeader title={title} subtitle={subtitle} />

      <SectionCard>
        <LoadingState message={message} />
      </SectionCard>
    </div>
  );
}
