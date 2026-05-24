"use client";

import { useState } from "react";

import FormLayout from "./FormLayout";
import FormGrid from "./FormGrid";
import FormField from "./FormField";
import TextInput from "./TextInput";
import SelectInput from "./SelectInput";
import TextareaInput from "./TextareaInput";
import SubmitButton from "./SubmitButton";
import FormError from "./FormError";
import FormSuccess from "./FormSuccess";
import { createReport } from "@/lib/api/reports";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import {
  reportFormDefaults,
  validateReportForm,
  type ReportFormValues,
} from "@/lib/validation/reportSchemas";

type CreateReportFormProps = {
  onSuccess?: () => void;
};

export default function CreateReportForm({
  onSuccess,
}: CreateReportFormProps) {
  const [values, setValues] =
    useState<ReportFormValues>(reportFormDefaults);

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createReport,
    onSuccess: () => {
      setValues(reportFormDefaults);
      onSuccess?.();
    },
  });

  function updateField(
    field: keyof ReportFormValues,
    value: string
  ) {
    setValues((current) => ({
      ...current,
      [field]: value,
    }));
  }

  return (
    <FormLayout title="Create Daily Report">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          handleSubmit(
            validateReportForm(values),
            "Daily report created successfully"
          );
        }}
        className="flex flex-col gap-8"
      >
        <FormGrid>
          <FormField
            label="Work Order ID"
            error={validationErrors.work_order_id}
          >
            <TextInput
              value={values.work_order_id}
              onChange={(event) =>
                updateField(
                  "work_order_id",
                  event.target.value
                )
              }
              placeholder="1"
            />
          </FormField>

          <FormField
            label="Reported By"
            error={validationErrors.reported_by}
          >
            <TextInput
              value={values.reported_by}
              onChange={(event) =>
                updateField(
                  "reported_by",
                  event.target.value
                )
              }
              placeholder="Engineer Name"
            />
          </FormField>

          <FormField
            label="Actual Quantity"
            error={validationErrors.actual_qty}
          >
            <TextInput
              type="number"
              value={values.actual_qty}
              onChange={(event) =>
                updateField(
                  "actual_qty",
                  event.target.value
                )
              }
              placeholder="150"
            />
          </FormField>

          <FormField
            label="Manpower Count"
            error={validationErrors.manpower_count}
          >
            <TextInput
              type="number"
              value={values.manpower_count}
              onChange={(event) =>
                updateField(
                  "manpower_count",
                  event.target.value
                )
              }
              placeholder="12"
            />
          </FormField>

          <FormField
            label="Equipment Hours"
            error={validationErrors.equipment_hours}
          >
            <TextInput
              type="number"
              value={values.equipment_hours}
              onChange={(event) =>
                updateField(
                  "equipment_hours",
                  event.target.value
                )
              }
              placeholder="8"
            />
          </FormField>

          <FormField
            label="Material Consumption"
            error={validationErrors.material_consumption}
          >
            <TextInput
              value={values.material_consumption}
              onChange={(event) =>
                updateField(
                  "material_consumption",
                  event.target.value
                )
              }
              placeholder="Concrete / Steel"
            />
          </FormField>

          <FormField
            label="Weather Status"
            error={validationErrors.weather_status}
          >
            <SelectInput
              value={values.weather_status}
              onChange={(event) =>
                updateField(
                  "weather_status",
                  event.target.value
                )
              }
              options={["Good", "Normal", "Bad"]}
            />
          </FormField>

          <FormField
            label="Report Status"
            error={validationErrors.report_status}
          >
            <SelectInput
              value={values.report_status}
              onChange={(event) =>
                updateField(
                  "report_status",
                  event.target.value
                )
              }
              options={["Draft", "Submitted", "Approved"]}
            />
          </FormField>
        </FormGrid>

        <FormField label="Delay Reason">
          <TextareaInput
            value={values.delay_reason}
            onChange={(event) =>
              updateField(
                "delay_reason",
                event.target.value
              )
            }
            placeholder="Describe delay reason..."
          />
        </FormField>

        <FormField label="Approved By">
          <TextInput
            value={values.approved_by}
            onChange={(event) =>
              updateField(
                "approved_by",
                event.target.value
              )
            }
            placeholder="Project Manager"
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton
          title="Submit Report"
          loading={isSubmitting}
        />
      </form>
    </FormLayout>
  );
}
