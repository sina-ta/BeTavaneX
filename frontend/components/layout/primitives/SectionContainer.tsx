import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
};

export default function SectionContainer({
  children,
  className = "",
}: Props) {
  return (
    <div className={`section-container page-wrapper ${className}`.trim()}>
      {children}
    </div>
  );
}
