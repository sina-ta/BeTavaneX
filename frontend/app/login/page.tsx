"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { setSessionActive } from "@/lib/auth/session";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <main className="auth-page">
      <div className="auth-brand-panel">
        <div className="logo-circle" style={{ width: 64, height: 64, fontSize: 28 }}>
          B
        </div>

        <h2
          style={{
            fontSize: 36,
            fontWeight: 800,
            marginTop: 32,
            marginBottom: 16,
            letterSpacing: "-0.02em",
          }}
        >
          BetavanX
        </h2>

        <p style={{ color: "#94a3b8", fontSize: 17, lineHeight: 1.7, maxWidth: 400 }}>
          Enterprise construction intelligence command center for
          daily operations, project control, and investor visibility.
        </p>

        <ul
          style={{
            marginTop: 40,
            padding: 0,
            listStyle: "none",
            display: "flex",
            flexDirection: "column",
            gap: 12,
            color: "#cbd5e1",
            fontSize: 14,
          }}
        >
          <li>✓ Operational KPI monitoring</li>
          <li>✓ Daily reports & work orders</li>
          <li>✓ Progress & delay visibility</li>
          <li>✓ Validation & lifecycle engines</li>
        </ul>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card">
          <h1>Sign in</h1>
          <p>Access your project command center</p>

          <form
            className="flex flex-col gap-5"
            onSubmit={(e) => {
              e.preventDefault();

              if (email && password) {
                setSessionActive(true);
                router.push("/dashboard/overview");
              }
            }}
          >
            <div className="input-group">
              <label className="input-label" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="operator@betavanx.com"
                className="input-base"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                className="input-base"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className="button-primary w-full">
              Enter Command Center
            </button>
          </form>

          <p style={{ marginTop: 24, fontSize: 14, color: "#64748b" }}>
            <Link href="/" className="text-blue-400 hover:underline">
              ← Back to home
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
