"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import KpiCard from "@/components/KpiCard";

import RecommendationCard from "@/components/RecommendationCard";

import Badge from "@/components/ui/Badge";

import PageHeader from "@/components/ui/PageHeader";

import SectionCard from "@/components/ui/SectionCard";

import TasksTable from "@/components/tables/TasksTable";

type DashboardData = {
  summary: {
    total_work_orders: number;
    total_reports: number;
    avg_cpi: number;
    avg_spi: number;
  };

  tasks: {
    task_id: number;
    progress_percent: number;
    cpi: number;
    spi: number;
    alert: string;

    recommendation?: {
      title: string;
      action: string;
    };
  }[];
};

export default function OverviewPage() {

  const [dashboardData, setDashboardData] =
    useState<DashboardData | null>(null);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/dashboard")

      .then((res) => res.json())

      .then((data) => {

        setDashboardData(data);

      })

      .catch((err) => {

        console.log(err);

      });

  }, []);

  if (!dashboardData) {

    return (

      <div className="page-wrapper">

        <PageHeader
          title="Project Overview"
          subtitle="
            Loading dashboard analytics
            and project intelligence...
          "
        />

        <SectionCard>

          <div className="loading-state">

            <div className="loading-spinner" />

            <div>
              Loading dashboard...
            </div>

          </div>

        </SectionCard>

      </div>
    );
  }

  return (

    <div className="page-wrapper">

      {/* PAGE HEADER */}

      <PageHeader
        title="Project Overview"
        subtitle="
          Real-time construction
          performance and project
          intelligence dashboard
        "
      />

      {/* RECOMMENDATION */}

      {dashboardData.tasks?.[0]
        ?.recommendation && (

        <RecommendationCard
          title={
            dashboardData.tasks[0]
              .recommendation!.title
          }
          message={
            dashboardData.tasks[0]
              .recommendation!.action
          }
        />
      )}

      {/* KPI GRID */}

      <div className="kpi-grid">

        <KpiCard
          title="Total Work Orders"
          value={
            dashboardData.summary
              .total_work_orders
          }
          footer="+12%"
        />

        <KpiCard
          title="Total Reports"
          value={
            dashboardData.summary
              .total_reports
          }
          footer="+8%"
        />

        <KpiCard
          title="Budget Health"
          value={
            Number(
              dashboardData.summary
                .avg_cpi
            ).toFixed(2)
          }
          footer="Healthy"
        />

        <KpiCard
          title="Project Speed"
          value={
            Number(
              dashboardData.summary
                .avg_spi
            ).toFixed(2)
          }
          footer="On Track"
        />

      </div>

      {/* TASK TABLE */}

      <TasksTable
        tasks={dashboardData.tasks}
      />
    </div>
  );
}