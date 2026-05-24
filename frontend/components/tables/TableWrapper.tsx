import DenseTableWrapper from "@/components/layout/primitives/DenseTableWrapper";
import CompactCard from "@/components/layout/primitives/CompactCard";

type Props = {
  title?: string;
  children: React.ReactNode;
};

export default function TableWrapper({
  title,
  children,
}: Props) {
  return (
    <CompactCard title={title}>
      <DenseTableWrapper>{children}</DenseTableWrapper>
    </CompactCard>
  );
}
