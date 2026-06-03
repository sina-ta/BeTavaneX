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
import EntitySelect from "@/components/console/EntitySelect";
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { createLocation } from "@/lib/api/phase1/planning";
import type { Location, LocationCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const LOCATION_STATUSES = ["ACTIVE", "CLOSED"];

export default function CreateLocationForm() {
  const { locations, addLocation, bumpRefresh } = useOperational();
  const { selectedProjectId } = useProject();

  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [level, setLevel] = useState("1");
  const [parentId, setParentId] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<LocationCreate, Location>({
      submit: createLocation,
      onSuccess: (item) => {
        addLocation(item);
        bumpRefresh();
        setCode("");
        setName("");
        setLevel("1");
        setParentId("");
        setStatus("ACTIVE");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="3 · Create Location" />;
  }

  const parentOptions = locations
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({ value: item.id, label: `${item.code} · ${item.name}` }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!code.trim()) errors.code = "Code is required";
    if (!name.trim()) errors.name = "Name is required";
    const levelNumber = Number(level);
    if (!Number.isInteger(levelNumber) || levelNumber < 1) {
      errors.level = "Level must be a positive integer";
    }

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: LocationCreate = {
      project_id: selectedProjectId as string,
      code: code.trim(),
      name: name.trim(),
      level: levelNumber,
      status,
      parent_id: parentId || null,
    };

    handleSubmit({ success: true, data: payload }, "Location created");
  }

  return (
    <FormLayout title="3 · Create Location">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="LOC-01"
            />
          </FormField>

          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Tower A · Level 3"
            />
          </FormField>

          <FormField label="Level" error={validationErrors.level}>
            <TextInput
              type="number"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              placeholder="1"
            />
          </FormField>

          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={LOCATION_STATUSES}
            />
          </FormField>

          <EntitySelect
            label="Parent Location (optional)"
            value={parentId}
            onChange={setParentId}
            options={parentOptions}
            placeholder="None (root)"
          />
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Create Location" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
