import type { ReactNode } from "react";

type Props = {
  title?: string;
  children: ReactNode;
  className?: string;
  flush?: boolean;
};

export default function CompactCard({
  title,
  children,
  className = "",
  flush = false,
}: Props) {
  return (
    <section
      className={`compact-card ${flush ? "compact-card--flush" : ""} ${className}`.trim()}
    >
      {title && (
        <header className="compact-card__header">
          <h2 className="compact-card__title">{title}</h2>
        </header>
      )}

      <div className="compact-card__body">{children}</div>
    </section>
  );
}
