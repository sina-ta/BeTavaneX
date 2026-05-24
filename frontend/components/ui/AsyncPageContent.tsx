import type { ReactNode } from "react";
import type { AsyncPageStatus } from "@/types/common";
import PageHeader from "./PageHeader";
import PageLoader from "./PageLoader";
import ErrorState from "./ErrorState";
import EmptyState from "./EmptyState";
import SectionCard from "./SectionCard";

type AsyncPageContentProps<T> = {
  status: AsyncPageStatus;
  data: T | null;
  error: string | null;
  loadingTitle: string;
  loadingSubtitle: string;
  loadingMessage?: string;
  emptyTitle?: string;
  onRetry?: () => void;
  isEmpty?: (data: T) => boolean;
  children: (data: T) => ReactNode;
};

export default function AsyncPageContent<T>({
  status,
  data,
  error,
  loadingTitle,
  loadingSubtitle,
  loadingMessage,
  emptyTitle = "No data available",
  onRetry,
  isEmpty,
  children,
}: AsyncPageContentProps<T>) {
  if (status === "loading") {
    return (
      <PageLoader
        title={loadingTitle}
        subtitle={loadingSubtitle}
        message={loadingMessage}
      />
    );
  }

  if (status === "error") {
    return (
      <div className="page-wrapper">
        <PageHeader
          title={loadingTitle}
          subtitle={loadingSubtitle}
        />

        <SectionCard>
          <ErrorState
            message={error ?? "Failed to load data"}
            onRetry={onRetry}
          />
        </SectionCard>
      </div>
    );
  }

  if (
    status === "empty" ||
    !data ||
    isEmpty?.(data)
  ) {
    return (
      <div className="page-wrapper">
        <PageHeader
          title={loadingTitle}
          subtitle={loadingSubtitle}
        />

        <SectionCard>
          <EmptyState title={emptyTitle} />
        </SectionCard>
      </div>
    );
  }

  return <>{children(data)}</>;
}
