"use client";

import KpiCard from "@/components/KpiCard";

import StatusBadge from "@/components/StatusBadge";

import RecommendationCard from "@/components/RecommendationCard";

import { useEffect, useState } from "react";

import ReportsTable from "@/components/ReportsTable";

type TaskDetail = {

  task_id: number;

  assigned_to: string;

  planned_qty: number;

  status: string;

  cpi: number;

  spi: number;

  progress_percent: number;

  alert: string;

  recommendation: {
    title: string;
    action: string;
  };

  reports: any[];
};

export default function TaskDetailPage({

  params,

}: any) {

  const [taskData, setTaskData] =
    useState<TaskDetail | null>(null);

  useEffect(() => {
    const taskId = window.location.pathname.split("/").pop();

    fetch(
   `http://127.0.0.1:8000/task/${taskId}`
    )
      .then((res) => res.json())
      .then((data) => {

        setTaskData(data);
      });

 }, []);

  if (!taskData) {

    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">


        <div className="space-y-8">

        {/* TITLE */}

        <div>

            <h1 className="text-4xl font-bold text-gray-800">

            Task {taskData.task_id}

            </h1>

            <p className="text-gray-500 mt-2">

            Assigned To:
            {" "}
            {taskData.assigned_to}

            </p>

        </div>

        {/* KPI SECTION */}
        <div className="grid grid-cols-4 gap-6">

            <KpiCard
                title="Progress"
                value={`${taskData.progress_percent.toFixed(1)}%`}
            />

            <KpiCard
                title="CPI"
                value={taskData.cpi.toFixed(2)}
            />

            <KpiCard
                title="SPI"
                value={taskData.spi.toFixed(2)}
            />

            <div className="card">

                <p className="metric-label">
                Status
                </p>

                <StatusBadge
                status={taskData.alert}
                />

            </div>

        </div>

        {/* RECOMMENDATION */}

        <RecommendationCard
            title={taskData.recommendation.title}
            message={taskData.recommendation.action}
        />
        {/* REPORT TABLE */}

        <ReportsTable reports={taskData.reports} />

        </div>
     </div>    

  );
}