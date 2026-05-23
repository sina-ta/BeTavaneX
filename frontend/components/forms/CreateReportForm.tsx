"use client";

import FormLayout from "./FormLayout";

import FormGrid from "./FormGrid";

import FormField from "./FormField";

import TextInput from "./TextInput";

import SelectInput from "./SelectInput";

import TextareaInput from "./TextareaInput";

import SubmitButton from "./SubmitButton";

export default function CreateReportForm() {

  function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    console.log(
      "Daily Report Submitted"
    );
  }

  return (

    <FormLayout title="Create Daily Report">

      <form
        onSubmit={handleSubmit}
        className="
          flex
          flex-col
          gap-8
        "
      >

        <FormGrid>

          <FormField
            label="Work Order ID"
          >

            <TextInput
              placeholder="WO-102"
            />

          </FormField>

          <FormField
            label="Reported By"
          >

            <TextInput
              placeholder="Engineer Name"
            />

          </FormField>

          <FormField
            label="Actual Quantity"
          >

            <TextInput
              type="number"
              placeholder="150"
            />

          </FormField>

          <FormField
            label="Manpower Count"
          >

            <TextInput
              type="number"
              placeholder="12"
            />

          </FormField>

          <FormField
            label="Equipment Hours"
          >

            <TextInput
              type="number"
              placeholder="8"
            />

          </FormField>

          <FormField
            label="Material Consumption"
          >

            <TextInput
              placeholder="Concrete / Steel"
            />

          </FormField>

          <FormField
            label="Weather Status"
          >

            <SelectInput
              options={[
                "Good",
                "Normal",
                "Bad",
              ]}
            />

          </FormField>

          <FormField
            label="Report Status"
          >

            <SelectInput
              options={[
                "Draft",
                "Submitted",
                "Approved",
              ]}
            />

          </FormField>

        </FormGrid>

        <FormField
          label="Delay Reason"
        >

          <TextareaInput
            placeholder="
              Describe delay reason...
            "
          />

        </FormField>

        <FormField
          label="Approved By"
        >

          <TextInput
            placeholder="Project Manager"
          />

        </FormField>

        <SubmitButton
          title="Submit Report"
        />

      </form>

    </FormLayout>
  );
}