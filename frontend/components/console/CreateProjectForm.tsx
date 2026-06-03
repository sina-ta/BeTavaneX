"use client";

import { useState } from "react";

import FormLayout from "@/components/forms/FormLayout";
import FormGrid from "@/components/forms/FormGrid";
import FormField from "@/components/forms/FormField";
import TextInput from "@/components/forms/TextInput";
import SelectInput from "@/components/forms/SelectInput";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import { createProject } from "@/lib/api/phase1/planning";
import type { Project, ProjectCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const PROJECT_STATUSES = [
  "DRAFT",
  "ACTIVE",
  "ON_HOLD",
  "COMPLETED",
  "CANCELLED",
];

export default function CreateProjectForm() {
  const { addProject, bumpRefresh } = useOperational();
  const { setSelectedProjectId } = useProject();

  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("ACTIVE");
  const [plannedStart, setPlannedStart] = useState("");
  const [plannedFinish, setPlannedFinish] = useState("");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<ProjectCreate, Project>({
      submit: createProject,
      onSuccess: (project) => {
        addProject(project);
        setSelectedProjectId(project.id);
        bumpRefresh();
        setCode("");
        setName("");
        setDescription("");
        setStatus("ACTIVE");
        setPlannedStart("");
        setPlannedFinish("");
      },
    });

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!code.trim()) errors.code = "Code is required";
    if (!name.trim()) errors.name = "Name is required";

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: ProjectCreate = {
      code: code.trim(),
      name: name.trim(),
      status,
      description: description.trim() || null,
      planned_start: plannedStart || null,
      planned_finish: plannedFinish || null,
    };

    handleSubmit(
      { success: true, data: payload },
      "Project created and selected"
    );
  }

  return (
    <FormLayout title="1 · Create Project">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="PRJ-001"
            />
          </FormField>

          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Residential Tower A"
            />
          </FormField>

          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={PROJECT_STATUSES}
            />
          </FormField>

          <FormField label="Planned Start">
            <TextInput
              type="date"
              value={plannedStart}
              onChange={(e) => setPlannedStart(e.target.value)}
            />
          </FormField>

          <FormField label="Planned Finish">
            <TextInput
              type="date"
              value={plannedFinish}
              onChange={(e) => setPlannedFinish(e.target.value)}
            />
          </FormField>

          <FormField label="Description">
            <TextInput
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional"
            />
          </FormField>
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Create Project" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
