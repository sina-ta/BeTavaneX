"use client";

import { useEffect, useState } from "react";

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

      {/* KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

        <div className="card p-6">
          <p className="card-title">Total Work Orders</p>

          <h2 className="card-value mt-2">
            {dashboardData.summary.total_work_orders}
          </h2>
        </div>

        <div className="card p-6">
          <p className="card-title">Total Reports</p>

          <h2 className="card-value mt-2">
            {dashboardData.summary.total_reports}
          </h2>
        </div>

        <div className="card p-6">
          <p className="card-title">Average CPI</p>

          <h2 className="card-value mt-2">
            {dashboardData.summary.avg_cpi}
          </h2>
        </div>

        <div className="card p-6">
          <p className="card-title">Average SPI</p>

          <h2 className="card-value mt-2">
            {dashboardData.summary.avg_spi}
          </h2>
        </div>

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
              <th className="p-3">Progress</th>
              <th className="p-3">CPI</th>
              <th className="p-3">SPI</th>
              <th className="p-3">Alert</th>

            </tr>

          </thead>

          <tbody>

            {dashboardData.tasks.map((task: any) => (

              <tr
                key={task.task_id}
                className="border-b hover:bg-gray-50 text-gray-700"
              >

                <td className="p-3 font-semibold">
                  {task.task_id}
                </td>

                <td className="p-3">
                  {task.progress_percent}%
                </td>

                <td className="p-3">
                  {task.cpi}
                </td>

                <td className="p-3">
                  {task.spi}
                </td>

                <td className="p-3">

                  <span
                    className={
                      task.alert.includes("Critical")
                        ? "critical"
                        : task.alert.includes("Warning")
                        ? "warning"
                        : "good"
                    } 
                  >
                    {task.alert}
                  </span>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );
}