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
import { createWBSItem } from "@/lib/api/phase1/planning";
import type { WBSItem, WBSItemCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const WBS_STATUSES = ["ACTIVE", "COMPLETED", "CANCELLED"];

export default function CreateWBSItemForm() {
  const { wbsItems, addWBSItem, bumpRefresh } = useOperational();
  const { selectedProjectId } = useProject();

  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [level, setLevel] = useState("1");
  const [parentId, setParentId] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<WBSItemCreate, WBSItem>({
      submit: createWBSItem,
      onSuccess: (item) => {
        addWBSItem(item);
        bumpRefresh();
        setCode("");
        setName("");
        setLevel("1");
        setParentId("");
        setStatus("ACTIVE");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="2 · Create WBS Item" />;
  }

  const parentOptions = wbsItems
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

    const payload: WBSItemCreate = {
      project_id: selectedProjectId as string,
      code: code.trim(),
      name: name.trim(),
      level: levelNumber,
      status,
      parent_id: parentId || null,
    };

    handleSubmit({ success: true, data: payload }, "WBS item created");
  }

  return (
    <FormLayout title="2 · Create WBS Item">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="WBS-01"
            />
          </FormField>

          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Substructure"
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
              options={WBS_STATUSES}
            />
          </FormField>

          <EntitySelect
            label="Parent WBS (optional)"
            value={parentId}
            onChange={setParentId}
            options={parentOptions}
            placeholder="None (root)"
          />
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Create WBS Item" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
