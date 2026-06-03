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
import { createActivityInstance } from "@/lib/api/phase1/planning";
import type {
  ActivityInstance,
  ActivityInstanceCreate,
} from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const ACTIVITY_STATUSES = ["ACTIVE", "COMPLETED", "CANCELLED"];

export default function CreateActivityInstanceForm() {
  const {
    wbsItems,
    locations,
    addActivityInstance,
    bumpRefresh,
  } = useOperational();
  const { selectedProjectId } = useProject();

  const [wbsItemId, setWbsItemId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [plannedStart, setPlannedStart] = useState("");
  const [plannedFinish, setPlannedFinish] = useState("");
  const [durationDays, setDurationDays] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<ActivityInstanceCreate, ActivityInstance>({
      submit: createActivityInstance,
      onSuccess: (item) => {
        addActivityInstance(item);
        bumpRefresh();
        setCode("");
        setName("");
        setPlannedStart("");
        setPlannedFinish("");
        setDurationDays("");
        setStatus("ACTIVE");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="4 · Create Activity Instance" />;
  }

  const wbsOptions = wbsItems
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({ value: item.id, label: `${item.code} · ${item.name}` }));
  const locationOptions = locations
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({ value: item.id, label: `${item.code} · ${item.name}` }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!wbsItemId) errors.wbs_item_id = "Select a WBS item";
    if (!locationId) errors.location_id = "Select a location";
    if (!code.trim()) errors.code = "Code is required";
    if (!name.trim()) errors.name = "Name is required";

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: ActivityInstanceCreate = {
      project_id: selectedProjectId as string,
      wbs_item_id: wbsItemId,
      location_id: locationId,
      code: code.trim(),
      name: name.trim(),
      status,
      planned_start: plannedStart || null,
      planned_finish: plannedFinish || null,
      planned_duration_days: durationDays ? Number(durationDays) : null,
    };

    handleSubmit({ success: true, data: payload }, "Activity instance created");
  }

  return (
    <FormLayout title="4 · Create Activity Instance">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <EntitySelect
            label="WBS Item"
            value={wbsItemId}
            onChange={setWbsItemId}
            options={wbsOptions}
            error={validationErrors.wbs_item_id}
          />

          <EntitySelect
            label="Location"
            value={locationId}
            onChange={setLocationId}
            options={locationOptions}
            error={validationErrors.location_id}
          />

          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="ACT-01"
            />
          </FormField>

          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Pour foundation slab"
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

          <FormField label="Planned Duration (days)">
            <TextInput
              type="number"
              value={durationDays}
              onChange={(e) => setDurationDays(e.target.value)}
              placeholder="10"
            />
          </FormField>

          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={ACTIVITY_STATUSES}
            />
          </FormField>
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton
          title="Create Activity Instance"
          loading={isSubmitting}
        />
      </form>
    </FormLayout>
  );
}
