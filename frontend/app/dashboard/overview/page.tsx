"use client";

import { useEffect, useState } from "react";

import KpiCard from "@/components/KpiCard";

import ProgressBar from "@/components/ProgressBar";

import StatusBadge from "@/components/StatusBadge";

import RecommendationCard from "@/components/RecommendationCard";

import Link from "next/link";

export default function OverviewPage() {

  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/dashboard")
      .then((res) => res.json())
      .then((data) => {
        setDashboardData(data);
      });

  }, []);

  if (!dashboardData) {

    return <div>Loading...</div>;
  }

  return (

    <div className="space-y-8">

      {/* TITLE */}
      <h1 className="page-title">
        Project Overview
      </h1>
     
      <RecommendationCard
        title={dashboardData.tasks[0].recommendation.title}
        message={dashboardData.tasks[0].recommendation.action}
      />

      {/* KPI CARDS */}
       <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

        <KpiCard
          title="Total Work Orders"
          value={dashboardData.summary.total_work_orders}
        />

        <KpiCard
          title="Total Reports"
          value={dashboardData.summary.total_reports}
        />

        <KpiCard
          title="Budget Health"
          value={dashboardData.summary.avg_cpi}
        />

        <KpiCard
          title="Project Speed"
          value={dashboardData.summary.avg_spi}
        />

      </div>

      {/* TASK TABLE */}
      <div className="table-container">

        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Project Tasks
        </h2>

        <table className="w-full">

          <thead>

            <tr className="border-b text-left table-header">

              <th className="p-3">Task</th>
              <th className="p-3">Schedule Progress</th>
              <th className="p-3">Budget Health</th>
              <th className="p-3">Project Speed</th>
              <th className="p-3">Alert</th>
              <th className="p-3">Recommendation</th>

            </tr>

          </thead>

          <tbody>

            {dashboardData.tasks.map((task: any) => (

              <tr
                key={task.task_id}
                className="border-b hover:bg-gray-50 text-gray-700"
              >

                <td className="p-3 font-semibold">
                  <Link
                    href={`/task/${task.task_id}`}
                    className="text-blue-600 font-semibold hover:underline"
                  >
                    {task.task_id}
                  </Link>
                </td>

                <td className="p-3 w-72">

                  <ProgressBar
                    value={task.progress_percent}
                  />

                </td>
                <td className="p-3">

                  <div className="font-semibold">

                    {
                      task.cpi >= 1
                        ? "🟢 Under Budget"
                        : "🟡 Over Budget"
                    }

                  </div>

                </td>

                <td className="p-3">

                  <div className="font-semibold">

                    {
                      task.spi >= 1
                        ? "⚡ Fast"
                        : "🐢 Delayed"
                    }

                  </div>

                </td>
                

                <td className="p-3">

                   <StatusBadge
                    status={task.alert}
                  />

                </td>
                <td className="p-3">

                  <div className="font-semibold text-gray-800">
                    {task.recommendation.title}
                  </div>

                  <div className="text-sm text-gray-500">
                    {task.recommendation.action}
                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );
}