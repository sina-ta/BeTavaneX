import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
};

export default function DenseTableWrapper({
  children,
  className = "",
}: Props) {
  return (
    <div className={`dense-table-wrapper ${className}`.trim()}>
      {children}
    </div>
  );
}
