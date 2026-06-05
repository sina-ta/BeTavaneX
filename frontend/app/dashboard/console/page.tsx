"use client";

import { useState } from "react";
import Link from "next/link";

import {
  createLocation,
  createProject,
  createWBSItem,
} from "@/lib/api/phase1/planning";
import RoleGate from "@/components/auth/RoleGate";
import { canPlan } from "@/lib/auth/role-policy";
import { useProject } from "@/lib/context/ProjectContext";
import { useWorkspace } from "@/lib/context/WorkspaceContext";
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
import KpiCard from "@/components/KpiCard";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import { useI18n } from "@/i18n/LanguageProvider";

const PROJECT_STATUSES = [
  "ACTIVE",
  "DRAFT",
  "ON_HOLD",
  "COMPLETED",
  "CANCELLED",
];

export default function OperationalConsolePage() {
  const { t } = useI18n();
  const {
    selectedProjectId,
    setSelectedProjectId,
    authorizedProjects,
    refreshAuthorizedProjects,
  } = useProject();
  const workspace = useWorkspace();

  const activeProject =
    authorizedProjects.find((p) => p.id === selectedProjectId) ??
    workspace.projects.find((p) => p.id === selectedProjectId) ??
    null;

  return (
    <SectionContainer>
      <PageHeader
        title={t("console_title")}
        subtitle={t("console_subtitle")}
        eyebrow={t("console_eyebrow")}
      />

      <SliceNav current="console" />

      <KPIGrid columns={4}>
        <KpiCard
          title={t("console_kpi_wbs")}
          value={workspace.wbsItems.length}
          icon="▦"
          iconTone="orange"
        />
        <KpiCard
          title={t("console_kpi_locations")}
          value={workspace.locations.length}
          icon="📍"
          iconTone="green"
        />
        <KpiCard
          title={t("console_kpi_activities")}
          value={workspace.activityInstances.length}
          icon="◎"
          iconTone="blue"
        />
        <KpiCard
          title={t("console_kpi_work_orders")}
          value={workspace.workOrders.length}
          icon="📋"
          iconTone="purple"
        />
      </KPIGrid>

      <RoleGate allow="plan">
        <DashboardGrid variant="split">
          <CreateProjectForm
            onCreated={async (project) => {
              workspace.addProject(project);
              setSelectedProjectId(project.id);
              await refreshAuthorizedProjects();
            }}
          />

          <CompactCard title={t("console_active_project")}>
            {activeProject ? (
              <p className="page-subtitle">
                <strong className="text-emphasis">
                  {activeProject.code} — {activeProject.name}
                </strong>
                <br />
                <span className="text-muted-inline">id: {activeProject.id}</span>
              </p>
            ) : (
              <p className="page-subtitle">{t("console_no_project")}</p>
            )}

            {authorizedProjects.length > 0 && (
              <div className="stack-sm" style={{ maxWidth: 480 }}>
                <FormField label={t("console_authorized_projects")}>
                  <EntitySelect
                    value={selectedProjectId ?? ""}
                    placeholder={t("console_select_project")}
                    onChange={(event) =>
                      setSelectedProjectId(event.target.value || null)
                    }
                    options={authorizedProjects.map((p) => ({
                      value: p.id,
                      label: `${p.code} — ${p.name}`,
                    }))}
                  />
                </FormField>
              </div>
            )}
          </CompactCard>
        </DashboardGrid>

        <DashboardGrid variant="split">
          <CreateWBSForm projectId={selectedProjectId} />
          <CreateLocationForm projectId={selectedProjectId} />
        </DashboardGrid>

        {selectedProjectId && (
          <p className="page-subtitle">
            {t("console_next_activity")}{" "}
            <Link href="/dashboard/console/activity" className="text-link">
              {t("console_nav_activity")}
            </Link>{" "}
            →{" "}
            <Link href="/dashboard/console/execution" className="text-link">
              {t("console_next_execution")}
            </Link>
          </p>
        )}
      </RoleGate>
    </SectionContainer>
  );
}

// ---------------------------------------------------------------------------

function CreateProjectForm({
  onCreated,
}: {
  onCreated: (project: import("@/lib/api/phase1/types").Project) => void | Promise<void>;
}) {
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createProject,
    onSuccess: async (project) => {
      await onCreated(project);
      setCode("");
      setName("");
      setDescription("");
      setStatus("ACTIVE");
    },
  });

  return (
    <FormLayout title="1 · Create Project">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!code.trim()) errors.code = "Code is required";
          if (!name.trim()) errors.name = "Name is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    code: code.trim(),
                    name: name.trim(),
                    description: description.trim() || null,
                    status,
                  },
                },
            "Project created"
          );
        }}
      >
        <FormGrid>
          <FormField label="Project Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="PRJ-001"
            />
          </FormField>
          <FormField label="Project Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Tower A"
            />
          </FormField>
          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={PROJECT_STATUSES}
            />
          </FormField>
        </FormGrid>

        <FormField label="Description">
          <TextareaInput
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional project description"
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Create Project" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function CreateWBSForm({ projectId }: { projectId: string | null }) {
  const workspace = useWorkspace();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [level, setLevel] = useState("1");
  const [parentId, setParentId] = useState("");
  const [description, setDescription] = useState("");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createWBSItem,
    onSuccess: (item) => {
      workspace.addWBSItem(item);
      setCode("");
      setName("");
      setParentId("");
      setDescription("");
    },
  });

  if (!projectId) {
    return (
      <FormLayout title="2 · Create WBS Item">
        <p className="page-subtitle">Select or create a project first.</p>
      </FormLayout>
    );
  }

  return (
    <FormLayout title="2 · Create WBS Item">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!code.trim()) errors.code = "Code is required";
          if (!name.trim()) errors.name = "Name is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    project_id: projectId,
                    code: code.trim(),
                    name: name.trim(),
                    level: Number(level) || 1,
                    parent_id: parentId || null,
                    description: description.trim() || null,
                  },
                },
            "WBS item created"
          );
        }}
      >
        <FormField label="Code" error={validationErrors.code}>
          <TextInput
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="WBS-1"
          />
        </FormField>
        <FormField label="Name" error={validationErrors.name}>
          <TextInput
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Structure"
          />
        </FormField>
        <FormField label="Level">
          <TextInput
            type="number"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            placeholder="1"
          />
        </FormField>
        <FormField label="Parent WBS (optional)">
          <EntitySelect
            value={parentId}
            placeholder="None (root)"
            onChange={(e) => setParentId(e.target.value)}
            options={workspace
              .wbsItemsForProject(projectId)
              .map((w) => ({ value: w.id, label: `${w.code} — ${w.name}` }))}
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Create WBS Item" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function CreateLocationForm({ projectId }: { projectId: string | null }) {
  const workspace = useWorkspace();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [level, setLevel] = useState("1");
  const [parentId, setParentId] = useState("");
  const [description, setDescription] = useState("");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createLocation,
    onSuccess: (item) => {
      workspace.addLocation(item);
      setCode("");
      setName("");
      setParentId("");
      setDescription("");
    },
  });

  if (!projectId) {
    return (
      <FormLayout title="3 · Create Location">
        <p className="page-subtitle">Select or create a project first.</p>
      </FormLayout>
    );
  }

  return (
    <FormLayout title="3 · Create Location">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!code.trim()) errors.code = "Code is required";
          if (!name.trim()) errors.name = "Name is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    project_id: projectId,
                    code: code.trim(),
                    name: name.trim(),
                    level: Number(level) || 1,
                    parent_id: parentId || null,
                    description: description.trim() || null,
                  },
                },
            "Location created"
          );
        }}
      >
        <FormField label="Code" error={validationErrors.code}>
          <TextInput
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="LOC-1"
          />
        </FormField>
        <FormField label="Name" error={validationErrors.name}>
          <TextInput
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Zone A"
          />
        </FormField>
        <FormField label="Level">
          <TextInput
            type="number"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            placeholder="1"
          />
        </FormField>
        <FormField label="Parent Location (optional)">
          <EntitySelect
            value={parentId}
            placeholder="None (root)"
            onChange={(e) => setParentId(e.target.value)}
            options={workspace
              .locationsForProject(projectId)
              .map((l) => ({ value: l.id, label: `${l.code} — ${l.name}` }))}
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Create Location" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

// ---------------------------------------------------------------------------

export function SliceNav({
  current,
}: {
  current: "console" | "activity" | "execution" | "runtime";
}) {
  const { t } = useI18n();

  const links: { href: string; label: string; key: string }[] = [
    ...(canPlan()
      ? [
          {
            href: "/dashboard/console",
            label: t("console_nav_bootstrap"),
            key: "console",
          },
          {
            href: "/dashboard/console/activity",
            label: t("console_nav_activity"),
            key: "activity",
          },
        ]
      : []),
    {
      href: "/dashboard/console/execution",
      label: canPlan()
        ? t("console_nav_execution")
        : t("nav_daily_reports"),
      key: "execution",
    },
    {
      href: "/dashboard/overview",
      label: t("console_nav_runtime"),
      key: "runtime",
    },
  ];

  return (
    <nav className="slice-nav" aria-label={t("console_title")}>
      {links.map((link) => (
        <Link
          key={link.key}
          href={link.href}
          className={`slice-nav__link ${
            current === link.key ? "is-active" : ""
          }`}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
