"use client";

import FormLayout from "@/components/forms/FormLayout";

export default function NoProjectNotice({ title }: { title: string }) {
  return (
    <FormLayout title={title}>
      <div className="panel-placeholder">
        <span>Create or select a project first (step 1).</span>
      </div>
    </FormLayout>
  );
}
