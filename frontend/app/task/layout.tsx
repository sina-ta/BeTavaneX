import PlatformShell from "@/components/layout/PlatformShell";

export default function TaskLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <PlatformShell>{children}</PlatformShell>;
}
