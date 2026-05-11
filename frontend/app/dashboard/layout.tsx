import Link from "next/link";
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-black text-white p-6">
        <h2 className="text-xl font-bold mb-6">BetavanX</h2>

        <nav className="space-y-4">
          <Link
             href="/dashboard/work-units"
            className="block hover:text-gray-300"
          >
            Work Units
         </Link>

          <Link 
            href="/dashboard/daily-work-orders"
            className="block hover:text-gray-300"
          >
            Daily Work Orders
          </Link>

          <Link href="/dashboard/daily-reports"
          className="block hover:text-gray-300"
          >
            Daily Reports
          </Link>
          <div>Overview</div>
          
          <div>Workers</div>
          <div>Performance</div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 bg-gray-100">
        {children}
      </main>
    </div>
  );
}