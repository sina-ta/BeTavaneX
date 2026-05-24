type Props = {
  title: string;
  subtitle?: string;
  eyebrow?: string;
};

export default function PageHeader({
  title,
  subtitle,
  eyebrow = "Operational Intelligence",
}: Props) {
  return (
    <header className="page-header-block">
      <span className="page-eyebrow">{eyebrow}</span>
      <h1 className="page-title">{title}</h1>
      {subtitle && (
        <p className="page-subtitle">{subtitle}</p>
      )}
    </header>
  );
}