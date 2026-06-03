"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { createWorkOrder } from "@/lib/api/phase1/planning";
import {
  approveWorkflowStep,
  assignWorkOrder,
  submitDailyReport,
} from "@/lib/api/phase1/runtime";
import RoleGate from "@/components/auth/RoleGate";
import {
  canApproveSteps,
  canAssignWorkOrders,
  canPlan,
  canSubmitDailyReports,
  getPhase1Role,
} from "@/lib/auth/role-policy";
import { useProject } from "@/lib/context/ProjectContext";
import { useWorkspace } from "@/lib/context/WorkspaceContext";
import {
  useProjectWorkflowStepOptions,
  useWorkOrders,
} from "@/lib/hooks/usePhase1Lists";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import FormField from "@/components/forms/FormField";
import FormGrid from "@/components/forms/FormGrid";
import FormLayout from "@/components/forms/FormLayout";
import TextInput from "@/components/forms/TextInput";
import SelectInput from "@/components/forms/SelectInput";
import TextareaInput from "@/components/forms/TextareaInput";
import EntitySelect from "@/components/forms/EntitySelect";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import { SliceNav } from "@/app/dashboard/console/page";

const WORK_ORDER_STATUSES = [
  "CREATED",
  "ASSIGNED",
  "IN_PROGRESS",
  "COMPLETED",
  "CANCELLED",
];
const REPORT_STATUSES = [
  "DRAFT",
  "SUBMITTED",
  "REVIEWED",
  "ACCEPTED",
  "REJECTED",
];

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

const FOCUS_SECTIONS = ["report", "assign", "approve", "work-order"] as const;
type FocusSection = (typeof FOCUS_SECTIONS)[number];

function isFocusSection(value: string | null): value is FocusSection {
  return FOCUS_SECTIONS.some((section) => section === value);
}

export default function ConsoleExecutionPage() {
  return (
    <Suspense
      fallback={
        <SectionContainer>
          <p className="page-subtitle">Loading execution workspace…</p>
        </SectionContainer>
      }
    >
      <ConsoleExecutionContent />
    </Suspense>
  );
}

function ConsoleExecutionContent() {
  const { selectedProjectId } = useProject();
  const searchParams = useSearchParams();
  const focusParam = searchParams.get("focus");
  const focus = isFocusSection(focusParam) ? focusParam : null;
  const role = getPhase1Role();

  useEffect(() => {
    if (!focus) {
      return;
    }
    const target = document.getElementById(`operational-${focus}`);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [focus, selectedProjectId]);

  const subtitle =
    role === "worker"
      ? "Submit today’s daily report for an assigned work order."
      : "Assign work orders, submit reports, and approve workflow steps.";

  return (
    <SectionContainer>
      <PageHeader
        title={role === "worker" ? "Field Reports" : "Execution & Approval"}
        subtitle={subtitle}
        eyebrow="Vertical Slice"
      />

      <SliceNav current="execution" />
      {selectedProjectId && (
        <ExecutionFocusNav focus={focus} role={role} />
      )}

      {!selectedProjectId ? (
        <CompactCard title="No project selected">
          <p className="page-subtitle">
            Go to{" "}
            <Link href="/dashboard/console" className="text-blue-400 hover:underline">
              Planning Bootstrap
            </Link>{" "}
            and select or create a project first.
          </p>
        </CompactCard>
      ) : role === "worker" ? (
        <div id="operational-report">
          <RoleGate allow="report">
            <DailyReportForm projectId={selectedProjectId} fastMode />
          </RoleGate>
        </div>
      ) : (
        <>
          <RoleGate allow="report">
            <div id="operational-report">
              <DailyReportForm projectId={selectedProjectId} fastMode />
            </div>
          </RoleGate>

          <DashboardGrid variant="split">
            <RoleGate allow="plan">
              <div id="operational-work-order">
                <CreateWorkOrderForm projectId={selectedProjectId} />
              </div>
            </RoleGate>
            <RoleGate allow="assign">
              <div id="operational-assign">
                <AssignWorkOrderForm projectId={selectedProjectId} />
              </div>
            </RoleGate>
          </DashboardGrid>

          <RoleGate allow="approve">
            <div id="operational-approve">
              <ApproveStepForm projectId={selectedProjectId} />
            </div>
          </RoleGate>
        </>
      )}
    </SectionContainer>
  );
}

function ExecutionFocusNav({
  focus,
  role,
}: {
  focus: FocusSection | null;
  role: ReturnType<typeof getPhase1Role>;
}) {
  const links: { id: FocusSection; label: string; show: boolean }[] = [
    {
      id: "report",
      label: "Daily report",
      show: canSubmitDailyReports(role),
    },
    {
      id: "assign",
      label: "Assign work order",
      show: canAssignWorkOrders(role),
    },
    {
      id: "approve",
      label: "Approve step",
      show: canApproveSteps(role),
    },
    {
      id: "work-order",
      label: "Create work order",
      show: canPlan(role),
    },
  ];

  const visible = links.filter((link) => link.show);
  if (visible.length < 2) {
    return null;
  }

  return (
    <nav className="operational-focus-nav" aria-label="Jump to task">
      {visible.map((link) => (
        <a
          key={link.id}
          href={`?focus=${link.id}`}
          className={focus === link.id ? "button-primary" : "button-ghost"}
        >
          {link.label}
        </a>
      ))}
    </nav>
  );
}

// ---------------------------------------------------------------------------

function CreateWorkOrderForm({ projectId }: { projectId: string }) {
  const workspace = useWorkspace();
  const { reload: reloadWorkOrders } = useWorkOrders(projectId);
  const [number, setNumber] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [plannedDate, setPlannedDate] = useState(today());
  const [status, setStatus] = useState("CREATED");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createWorkOrder,
    onSuccess: (workOrder) => {
      workspace.addWorkOrder(workOrder);
      void reloadWorkOrders();
      setNumber("");
      setTitle("");
      setDescription("");
    },
  });

  return (
    <FormLayout title="6 · Create Work Order">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!number.trim())
            errors.work_order_number = "Number is required";
          if (!title.trim()) errors.title = "Title is required";
          if (!plannedDate) errors.planned_date = "Planned date is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    project_id: projectId,
                    work_order_number: number.trim(),
                    title: title.trim(),
                    description: description.trim() || null,
                    planned_date: plannedDate,
                    status,
                  },
                },
            "Work order created"
          );
        }}
      >
        <FormGrid>
          <FormField
            label="Work Order Number"
            error={validationErrors.work_order_number}
          >
            <TextInput
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder="WO-001"
            />
          </FormField>
          <FormField label="Title" error={validationErrors.title}>
            <TextInput
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Slab pour crew"
            />
          </FormField>
          <FormField
            label="Planned Date"
            error={validationErrors.planned_date}
          >
            <TextInput
              type="date"
              value={plannedDate}
              onChange={(e) => setPlannedDate(e.target.value)}
            />
          </FormField>
          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={WORK_ORDER_STATUSES}
            />
          </FormField>
        </FormGrid>

        <FormField label="Description">
          <TextareaInput
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional work order description"
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Create Work Order" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function AssignWorkOrderForm({ projectId }: { projectId: string }) {
  const workspace = useWorkspace();
  const { refreshAuthorizedProjects } = useProject();
  const { data: workOrdersPage, reload: reloadWorkOrders } = useWorkOrders(projectId);
  const { options: stepOptions } = useProjectWorkflowStepOptions(projectId);
  const workOrderOptions = (workOrdersPage?.items ?? []).map((workOrder) => ({
    value: workOrder.id,
    label: `${workOrder.work_order_number} — ${workOrder.title}`,
  }));
  const [workOrderId, setWorkOrderId] = useState("");
  const [workflowStepId, setWorkflowStepId] = useState("");
  const [executionWeight, setExecutionWeight] = useState("100");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: (input: {
      workOrderId: string;
      workflowStepId: string;
      executionWeight: number;
    }) =>
      assignWorkOrder(input.workOrderId, {
        workflow_step_id: input.workflowStepId,
        execution_weight: input.executionWeight,
      }),
    onSuccess: (assignment) => {
      workspace.addAssignment(assignment);
      void reloadWorkOrders();
      void refreshAuthorizedProjects();
    },
  });

  return (
    <FormLayout title="7 · Assign Work Order → Step">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!workOrderId) errors.work_order_id = "Work order is required";
          if (!workflowStepId)
            errors.workflow_step_id = "Workflow step is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    workOrderId,
                    workflowStepId,
                    executionWeight: Number(executionWeight) || 0,
                  },
                },
            "Work order assigned to workflow step"
          );
        }}
      >
        <FormField label="Work Order" error={validationErrors.work_order_id}>
          <EntitySelect
            value={workOrderId}
            placeholder="Select work order…"
            onChange={(e) => setWorkOrderId(e.target.value)}
            options={
              workOrderOptions.length > 0
                ? workOrderOptions
                : workspace.workOrdersForProject(projectId).map((w) => ({
                    value: w.id,
                    label: `${w.work_order_number} — ${w.title}`,
                  }))
            }
          />
        </FormField>
        <FormField
          label="Workflow Step"
          error={validationErrors.workflow_step_id}
        >
          <EntitySelect
            value={workflowStepId}
            placeholder="Select workflow step…"
            onChange={(e) => setWorkflowStepId(e.target.value)}
            options={
              stepOptions.length > 0
                ? stepOptions
                : workspace
                    .workflowStepsForProject(projectId)
                    .map((s) => ({
                      value: s.id,
                      label: `${s.code} — ${s.name}`,
                    }))
            }
          />
        </FormField>
        <FormField label="Execution Weight (0–100)">
          <TextInput
            type="number"
            value={executionWeight}
            onChange={(e) => setExecutionWeight(e.target.value)}
            placeholder="100"
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Assign Work Order" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function DailyReportForm({
  projectId,
  fastMode = false,
}: {
  projectId: string;
  fastMode?: boolean;
}) {
  const workspace = useWorkspace();
  const { data: workOrdersPage, reload: reloadWorkOrders } = useWorkOrders(projectId);
  const workOrderOptions = (workOrdersPage?.items ?? []).map((workOrder) => ({
    value: workOrder.id,
    label: `${workOrder.work_order_number} — ${workOrder.title}`,
    updatedAt: workOrder.updated_at,
  }));
  const [workOrderId, setWorkOrderId] = useState("");
  const [showDetails, setShowDetails] = useState(!fastMode);
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

  useEffect(() => {
    if (workOrderId || workOrderOptions.length !== 1) {
      return;
    }
    setWorkOrderId(workOrderOptions[0].value);
  }, [workOrderId, workOrderOptions]);

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: submitDailyReport,
    onSuccess: (report) => {
      workspace.addDailyReport(report);
      void reloadWorkOrders();
      setSummary("");
      setExecutionNotes("");
      setIssueNotes("");
      setDelayNotes("");
      setWeatherNotes("");
      setEvidenceJson("");
    },
  });

  const title = fastMode ? "Submit Daily Report" : "8 · Submit Daily Report";

  return (
    <FormLayout title={title}>
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!workOrderId) errors.work_order_id = "Work order is required";
          if (!reportDate) errors.report_date = "Report date is required";

          let evidence: Record<string, unknown> | unknown[] | null = null;
          if (evidenceJson.trim()) {
            try {
              evidence = JSON.parse(evidenceJson);
            } catch {
              errors.evidence_metadata = "Evidence must be valid JSON";
            }
          }

          const selectedWorkOrder = (workOrdersPage?.items ?? []).find(
            (w) => w.id === workOrderId
          );

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    work_order_id: workOrderId,
                    report_date: reportDate,
                    expected_work_order_updated_at:
                      selectedWorkOrder?.updated_at ?? null,
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
                  },
                },
            "Daily report submitted"
          );
        }}
      >
        <FormField label="Work Order" error={validationErrors.work_order_id}>
          <EntitySelect
            value={workOrderId}
            placeholder="Select work order…"
            onChange={(e) => setWorkOrderId(e.target.value)}
            options={
              workOrderOptions.length > 0
                ? workOrderOptions
                : workspace.workOrdersForProject(projectId).map((w) => ({
                    value: w.id,
                    label: `${w.work_order_number} — ${w.title}`,
                  }))
            }
          />
        </FormField>
        {workOrderOptions.length === 0 && (
          <p className="page-subtitle">
            No work orders yet. Ask a supervisor to assign one, or refresh after
            assignment.
          </p>
        )}
        <FormGrid>
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
          {!fastMode && (
            <FormField label="Status">
              <SelectInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                options={REPORT_STATUSES}
              />
            </FormField>
          )}
        </FormGrid>

        <FormField label="Summary">
          <TextareaInput
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="What was done today (required for a useful report)"
            rows={fastMode ? 3 : 2}
          />
        </FormField>

        {fastMode && (
          <button
            type="button"
            className="button-ghost"
            onClick={() => setShowDetails((value) => !value)}
          >
            {showDetails ? "Hide extra fields" : "Add notes, counts, evidence"}
          </button>
        )}

        {showDetails && (
          <>
            {fastMode && (
              <FormField label="Status">
                <SelectInput
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  options={REPORT_STATUSES}
                />
              </FormField>
            )}
            <FormField label="Execution Notes">
              <TextareaInput
                value={executionNotes}
                onChange={(e) => setExecutionNotes(e.target.value)}
                placeholder="What was executed today"
              />
            </FormField>
            <FormGrid>
              <FormField label="Manpower">
                <TextInput
                  type="number"
                  value={manpower}
                  onChange={(e) => setManpower(e.target.value)}
                />
              </FormField>
              <FormField label="Equipment">
                <TextInput
                  type="number"
                  value={equipment}
                  onChange={(e) => setEquipment(e.target.value)}
                />
              </FormField>
              <FormField label="Material Entries">
                <TextInput
                  type="number"
                  value={materialEntries}
                  onChange={(e) => setMaterialEntries(e.target.value)}
                />
              </FormField>
            </FormGrid>
            <FormGrid>
              <FormField label="Issue Notes">
                <TextInput
                  value={issueNotes}
                  onChange={(e) => setIssueNotes(e.target.value)}
                />
              </FormField>
              <FormField label="Delay Notes">
                <TextInput
                  value={delayNotes}
                  onChange={(e) => setDelayNotes(e.target.value)}
                />
              </FormField>
              <FormField label="Weather Notes">
                <TextInput
                  value={weatherNotes}
                  onChange={(e) => setWeatherNotes(e.target.value)}
                />
              </FormField>
            </FormGrid>
            <FormField
              label="Evidence (JSON, optional)"
              error={validationErrors.evidence_metadata}
            >
              <TextareaInput
                value={evidenceJson}
                onChange={(e) => setEvidenceJson(e.target.value)}
                placeholder='{"photos": 3}'
                rows={2}
              />
            </FormField>
          </>
        )}

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Submit Daily Report" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function ApproveStepForm({ projectId }: { projectId: string }) {
  const workspace = useWorkspace();
  const { options: stepOptions } = useProjectWorkflowStepOptions(projectId);
  const [workflowStepId, setWorkflowStepId] = useState("");
  const [approvalType, setApprovalType] = useState("FINAL");
  const [approvalDate, setApprovalDate] = useState(today());
  const [approvalNotes, setApprovalNotes] = useState("");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: (input: {
      workflowStepId: string;
      approval_type: string;
      approval_date: string | null;
      approval_notes: string | null;
      expected_workflow_step_updated_at: string | null;
    }) =>
      approveWorkflowStep(input.workflowStepId, {
        approval_type: input.approval_type,
        approval_date: input.approval_date,
        approval_notes: input.approval_notes,
        expected_workflow_step_updated_at:
          input.expected_workflow_step_updated_at,
      }),
    onSuccess: (approval) => {
      workspace.addApproval(approval);
      setApprovalNotes("");
    },
  });

  return (
    <FormLayout title="9 · Approve Workflow Step">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!workflowStepId)
            errors.workflow_step_id = "Workflow step is required";

          const selected = stepOptions.find((o) => o.value === workflowStepId);

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    workflowStepId,
                    approval_type: approvalType.trim() || "FINAL",
                    approval_date: approvalDate || null,
                    approval_notes: approvalNotes.trim() || null,
                    expected_workflow_step_updated_at:
                      selected?.updatedAt ?? null,
                  },
                },
            "Workflow step approved"
          );
        }}
      >
        <FormField
          label="Workflow Step"
          error={validationErrors.workflow_step_id}
        >
          <EntitySelect
            value={workflowStepId}
            placeholder="Select workflow step…"
            onChange={(e) => setWorkflowStepId(e.target.value)}
            options={
              stepOptions.length > 0
                ? stepOptions
                : workspace
                    .workflowStepsForProject(projectId)
                    .map((s) => ({
                      value: s.id,
                      label: `${s.code} — ${s.name}`,
                    }))
            }
          />
        </FormField>
        <FormGrid>
          <FormField label="Approval Type">
            <TextInput
              value={approvalType}
              onChange={(e) => setApprovalType(e.target.value)}
              placeholder="FINAL"
            />
          </FormField>
          <FormField label="Approval Date">
            <TextInput
              type="date"
              value={approvalDate}
              onChange={(e) => setApprovalDate(e.target.value)}
            />
          </FormField>
        </FormGrid>
        <FormField label="Approval Notes">
          <TextareaInput
            value={approvalNotes}
            onChange={(e) => setApprovalNotes(e.target.value)}
            placeholder="Optional notes"
            rows={3}
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Approve Step" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
