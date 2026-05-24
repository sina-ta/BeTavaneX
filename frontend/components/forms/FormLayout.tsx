import CompactCard from "@/components/layout/primitives/CompactCard";

type Props = {
  title?: string;
  children: React.ReactNode;
};

export default function FormLayout({
  title,
  children,
}: Props) {
  return (
    <CompactCard title={title}>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
        {children}
      </div>
    </CompactCard>
  );
}
