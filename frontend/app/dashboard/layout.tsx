import PlatformShell from "@/components/layout/PlatformShell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <PlatformShell>{children}</PlatformShell>;
}
