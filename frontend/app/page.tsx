import Link from "next/link";

export default function Home() {
  return (
    <main className="landing-page">
      <div className="landing-logo">B</div>

      <div>
        <h1 className="landing-title">BetavanX</h1>
        <p className="landing-subtitle">
          Construction operational intelligence platform — monitor
          KPIs, daily reports, work orders, and workforce from one
          command center.
        </p>
      </div>

      <div className="landing-actions">
        <Link href="/login" className="button-primary">
          Sign in to Command Center
        </Link>
        <Link href="/dashboard/overview" className="button-ghost">
          View demo dashboard
        </Link>
      </div>
    </main>
  );
}
