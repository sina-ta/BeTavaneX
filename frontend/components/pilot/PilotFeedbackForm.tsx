"use client";

import { FormEvent, useState } from "react";

import { submitPilotFeedback } from "@/lib/api/phase1/pilot";
import type { PilotFeedbackCategory } from "@/lib/api/phase1/pilot";
import { useProject } from "@/lib/context/ProjectContext";
import CompactCard from "@/components/layout/primitives/CompactCard";

const CATEGORIES: { value: PilotFeedbackCategory; label: string }[] = [
  { value: "confusion", label: "Confusion" },
  { value: "blocker", label: "Blocker" },
  { value: "missing_flow", label: "Missing flow" },
  { value: "ux_pain", label: "UX pain" },
  { value: "gap", label: "Operational gap" },
  { value: "other", label: "Other" },
];

type PilotFeedbackFormProps = {
  pagePath?: string;
  bare?: boolean;
};

export default function PilotFeedbackForm({
  pagePath = "/dashboard/overview",
  bare = false,
}: PilotFeedbackFormProps) {
  const { selectedProjectId } = useProject();
  const [category, setCategory] =
    useState<PilotFeedbackCategory>("confusion");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">(
    "idle",
  );

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (message.trim().length < 3) {
      return;
    }
    setStatus("sending");
    try {
      await submitPilotFeedback({
        category,
        message: message.trim(),
        page_path: pagePath,
        project_id: selectedProjectId ?? undefined,
      });
      setMessage("");
      setStatus("ok");
    } catch {
      setStatus("error");
    }
  }

  const form = (
      <form onSubmit={handleSubmit} className="stack-sm">
        <label className="form-label">
          Category
          <select
            className="form-input"
            value={category}
            onChange={(e) =>
              setCategory(e.target.value as PilotFeedbackCategory)
            }
          >
            {CATEGORIES.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <label className="form-label">
          Note
          <textarea
            className="form-input"
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="What slowed you down or was unclear?"
            required
            minLength={3}
          />
        </label>
        <button
          type="submit"
          className="btn btn-secondary"
          disabled={status === "sending"}
        >
          {status === "sending" ? "Sending…" : "Submit feedback"}
        </button>
        {status === "ok" && (
          <p className="text-success">Recorded — thank you.</p>
        )}
        {status === "error" && (
          <p className="text-danger">Could not send. Try again when online.</p>
        )}
      </form>
  );

  if (bare) {
    return (
      <>
        <p className="page-subtitle" style={{ marginBottom: "0.75rem" }}>
          Report confusion, blockers, or gaps from the field.
        </p>
        {form}
      </>
    );
  }

  return (
    <CompactCard title="Pilot feedback">
      <p className="page-subtitle" style={{ marginBottom: "0.75rem" }}>
        Report confusion, blockers, or gaps during the controlled pilot.
      </p>
      {form}
    </CompactCard>
  );
}
