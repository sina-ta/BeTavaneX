"use client";

import { useEffect, useState } from "react";

import CreateReportForm from "@/components/CreateReportForm";

import ReportsListTable from "@/components/ReportsListTable";

export default function DailyReportsPage() {

  const [reports, setReports] = useState([]);

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

    <div className="space-y-8">

      <h1 className="page-title">

        Daily Reports

      </h1>

      <CreateReportForm
        onReportCreated={fetchReports}
      />

      <ReportsListTable reports={reports} />

    </div>
  );
}