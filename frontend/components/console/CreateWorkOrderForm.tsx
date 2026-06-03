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
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { createWorkOrder } from "@/lib/api/phase1/planning";
import type { WorkOrder, WorkOrderCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const WORK_ORDER_STATUSES = [
  "CREATED",
  "ASSIGNED",
  "IN_PROGRESS",
  "COMPLETED",
  "CANCELLED",
];

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function CreateWorkOrderForm() {
  const { addWorkOrder, bumpRefresh } = useOperational();
  const { selectedProjectId } = useProject();

  const [workOrderNumber, setWorkOrderNumber] = useState("");
  const [title, setTitle] = useState("");
  const [plannedDate, setPlannedDate] = useState(today());
  const [status, setStatus] = useState("CREATED");
  const [description, setDescription] = useState("");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<WorkOrderCreate, WorkOrder>({
      submit: createWorkOrder,
      onSuccess: (item) => {
        addWorkOrder(item);
        bumpRefresh();
        setWorkOrderNumber("");
        setTitle("");
        setPlannedDate(today());
        setStatus("CREATED");
        setDescription("");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="6 · Create Work Order" />;
  }

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!workOrderNumber.trim()) {
      errors.work_order_number = "Work order number is required";
    }
    if (!title.trim()) errors.title = "Title is required";
    if (!plannedDate) errors.planned_date = "Planned date is required";

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: WorkOrderCreate = {
      project_id: selectedProjectId as string,
      work_order_number: workOrderNumber.trim(),
      title: title.trim(),
      planned_date: plannedDate,
      status,
      description: description.trim() || null,
    };

    handleSubmit({ success: true, data: payload }, "Work order created");
  }

  return (
    <FormLayout title="6 · Create Work Order">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <FormField
            label="Work Order Number"
            error={validationErrors.work_order_number}
          >
            <TextInput
              value={workOrderNumber}
              onChange={(e) => setWorkOrderNumber(e.target.value)}
              placeholder="WO-001"
            />
          </FormField>

          <FormField label="Title" error={validationErrors.title}>
            <TextInput
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Daily concrete works"
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

        <SubmitButton title="Create Work Order" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
