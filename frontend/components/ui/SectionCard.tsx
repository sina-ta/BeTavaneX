import { ReactNode } from "react";

import CompactCard from "@/components/layout/primitives/CompactCard";

type Props = {
  title?: string;
  children: ReactNode;
  className?: string;
};

/** @deprecated Prefer CompactCard — kept for backward compatibility */
export default function SectionCard({
  title,
  children,
  className,
}: Props) {
  return (
    <CompactCard title={title} className={className}>
      {children}
    </CompactCard>
  );
}
