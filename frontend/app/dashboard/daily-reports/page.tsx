"use client";

import { useEffect, useState } from "react";

import CreateReportForm from "@/components/forms/CreateReportForm";

import ReportsTable from "@/components/tables/ReportsTable";

import PageHeader from "@/components/ui/PageHeader";

import SectionCard from "@/components/ui/SectionCard";

export default function DailyReportsPage() {

  const [reports, setReports] =
    useState([]);

  async function fetchReports() {

    const res = await fetch(
      "http://127.0.0.1:8000/daily-reports"
    );

    const data = await res.json();

    setReports(data);
  }

  useEffect(() => {

    fetchReports();

  }, []);

  return (

    <div className="page-wrapper">

      <PageHeader
        title="Daily Reports"
        subtitle="
          Create, review and
          monitor daily operational
          construction reports
        "
      />

      <CreateReportForm />

      <SectionCard
        title="Reports List"
      >

        <ReportsTable reports={reports} />

      </SectionCard>

    </div>
  );
}