"use client";

import { useState } from "react";

import FormLayout from "@/components/forms/FormLayout";
import FormGrid from "@/components/forms/FormGrid";
import FormField from "@/components/forms/FormField";
import TextInput from "@/components/forms/TextInput";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import EntitySelect from "@/components/console/EntitySelect";
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { assignWorkOrder } from "@/lib/api/phase1/runtime";
import type {
  WorkOrderAssignmentCreate,
  WorkOrderWorkflowStep,
} from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

type AssignInput = {
  workOrderId: string;
  payload: WorkOrderAssignmentCreate;
};

export default function AssignWorkOrderForm() {
  const {
    workOrders,
    workflowSteps,
    activityInstances,
    addAssignment,
    bumpRefresh,
  } = useOperational();
  const { selectedProjectId } = useProject();

  const [workOrderId, setWorkOrderId] = useState("");
  const [workflowStepId, setWorkflowStepId] = useState("");
  const [executionWeight, setExecutionWeight] = useState("1");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<AssignInput, WorkOrderWorkflowStep>({
      submit: ({ workOrderId: id, payload }) => assignWorkOrder(id, payload),
      onSuccess: (link) => {
        addAssignment(link);
        bumpRefresh();
        setExecutionWeight("1");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="7 · Assign Work Order" />;
  }

  const projectActivityIds = new Set(
    activityInstances
      .filter((item) => item.project_id === selectedProjectId)
      .map((item) => item.id)
  );

  const workOrderOptions = workOrders
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({
      value: item.id,
      label: `${item.work_order_number} · ${item.title}`,
    }));
  const stepOptions = workflowSteps
    .filter((step) => projectActivityIds.has(step.activity_instance_id))
    .map((step) => ({ value: step.id, label: `${step.code} · ${step.name}` }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!workOrderId) errors.work_order_id = "Select a work order";
    if (!workflowStepId) errors.workflow_step_id = "Select a workflow step";
    const weight = Number(executionWeight);
    if (!Number.isFinite(weight) || weight <= 0) {
      errors.execution_weight = "Execution weight must be greater than 0";
    }

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    handleSubmit(
      {
        success: true,
        data: {
          workOrderId,
          payload: {
            workflow_step_id: workflowStepId,
            execution_weight: weight,
          },
        },
      },
      "Work order assigned to workflow step"
    );
  }

  return (
    <FormLayout title="7 · Assign Work Order">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <EntitySelect
            label="Work Order"
            value={workOrderId}
            onChange={setWorkOrderId}
            options={workOrderOptions}
            error={validationErrors.work_order_id}
          />

          <EntitySelect
            label="Workflow Step"
            value={workflowStepId}
            onChange={setWorkflowStepId}
            options={stepOptions}
            error={validationErrors.workflow_step_id}
          />

          <FormField
            label="Execution Weight (> 0)"
            error={validationErrors.execution_weight}
          >
            <TextInput
              type="number"
              value={executionWeight}
              onChange={(e) => setExecutionWeight(e.target.value)}
              placeholder="1"
            />
          </FormField>
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Assign Work Order" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
