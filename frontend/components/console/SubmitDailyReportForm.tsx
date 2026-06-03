"use client";

import { useState } from "react";

import FormLayout from "@/components/forms/FormLayout";
import FormGrid from "@/components/forms/FormGrid";
import FormField from "@/components/forms/FormField";
import TextInput from "@/components/forms/TextInput";
import SelectInput from "@/components/forms/SelectInput";
import TextareaInput from "@/components/forms/TextareaInput";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import EntitySelect from "@/components/console/EntitySelect";
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { submitDailyReport } from "@/lib/api/phase1/runtime";
import type { DailyReport, DailyReportCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const DAILY_REPORT_STATUSES = [
  "DRAFT",
  "SUBMITTED",
  "REVIEWED",
  "ACCEPTED",
  "REJECTED",
];

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function SubmitDailyReportForm() {
  const { workOrders, addDailyReport, bumpRefresh } = useOperational();
  const { selectedProjectId } = useProject();

  const [workOrderId, setWorkOrderId] = useState("");
  const [reportDate, setReportDate] = useState(today());
  const [status, setStatus] = useState("SUBMITTED");
  const [summary, setSummary] = useState("");
  const [executionNotes, setExecutionNotes] = useState("");
  const [issueNotes, setIssueNotes] = useState("");
  const [delayNotes, setDelayNotes] = useState("");
  const [weatherNotes, setWeatherNotes] = useState("");
  const [manpower, setManpower] = useState("0");
  const [equipment, setEquipment] = useState("0");
  const [materialEntries, setMaterialEntries] = useState("0");
  const [evidenceJson, setEvidenceJson] = useState("");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<DailyReportCreate, DailyReport>({
      submit: submitDailyReport,
      onSuccess: (report) => {
        addDailyReport(report);
        bumpRefresh();
        setSummary("");
        setExecutionNotes("");
        setIssueNotes("");
        setDelayNotes("");
        setWeatherNotes("");
        setManpower("0");
        setEquipment("0");
        setMaterialEntries("0");
        setEvidenceJson("");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="8 · Submit Daily Report" />;
  }

  const workOrderOptions = workOrders
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({
      value: item.id,
      label: `${item.work_order_number} · ${item.title}`,
    }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!workOrderId) errors.work_order_id = "Select a work order";
    if (!reportDate) errors.report_date = "Report date is required";

    let evidence: Record<string, unknown> | unknown[] | null = null;
    if (evidenceJson.trim()) {
      try {
        evidence = JSON.parse(evidenceJson);
      } catch {
        errors.evidence_metadata = "Evidence must be valid JSON";
      }
    }

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: DailyReportCreate = {
      work_order_id: workOrderId,
      report_date: reportDate,
      status,
      summary: summary.trim() || null,
      execution_notes: executionNotes.trim() || null,
      issue_notes: issueNotes.trim() || null,
      delay_notes: delayNotes.trim() || null,
      weather_notes: weatherNotes.trim() || null,
      reported_manpower: Number(manpower) || 0,
      reported_equipment: Number(equipment) || 0,
      reported_material_entries: Number(materialEntries) || 0,
      evidence_metadata: evidence,
    };

    handleSubmit({ success: true, data: payload }, "Daily report submitted");
  }

  return (
    <FormLayout title="8 · Submit Daily Report">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <EntitySelect
            label="Work Order"
            value={workOrderId}
            onChange={setWorkOrderId}
            options={workOrderOptions}
            error={validationErrors.work_order_id}
          />

          <FormField
            label="Report Date"
            error={validationErrors.report_date}
          >
            <TextInput
              type="date"
              value={reportDate}
              onChange={(e) => setReportDate(e.target.value)}
            />
          </FormField>

          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={DAILY_REPORT_STATUSES}
            />
          </FormField>

          <FormField label="Manpower">
            <TextInput
              type="number"
              value={manpower}
              onChange={(e) => setManpower(e.target.value)}
              placeholder="12"
            />
          </FormField>

          <FormField label="Equipment">
            <TextInput
              type="number"
              value={equipment}
              onChange={(e) => setEquipment(e.target.value)}
              placeholder="3"
            />
          </FormField>

          <FormField label="Material Entries">
            <TextInput
              type="number"
              value={materialEntries}
              onChange={(e) => setMaterialEntries(e.target.value)}
              placeholder="5"
            />
          </FormField>
        </FormGrid>

        <FormField label="Summary">
          <TextInput
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Daily progress summary"
          />
        </FormField>

        <FormField label="Execution Notes">
          <TextareaInput
            value={executionNotes}
            onChange={(e) => setExecutionNotes(e.target.value)}
            placeholder="What was executed today…"
          />
        </FormField>

        <FormGrid>
          <FormField label="Issue Notes">
            <TextareaInput
              value={issueNotes}
              onChange={(e) => setIssueNotes(e.target.value)}
              placeholder="Issues encountered…"
            />
          </FormField>

          <FormField label="Delay Notes">
            <TextareaInput
              value={delayNotes}
              onChange={(e) => setDelayNotes(e.target.value)}
              placeholder="Delay reasons…"
            />
          </FormField>
        </FormGrid>

        <FormField label="Weather Notes">
          <TextInput
            value={weatherNotes}
            onChange={(e) => setWeatherNotes(e.target.value)}
            placeholder="Clear / rain / heat…"
          />
        </FormField>

        <FormField
          label="Evidence Metadata (JSON, optional)"
          error={validationErrors.evidence_metadata}
        >
          <TextareaInput
            value={evidenceJson}
            onChange={(e) => setEvidenceJson(e.target.value)}
            placeholder='{"photos": ["a.jpg"], "gps": "..."}'
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Submit Daily Report" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
