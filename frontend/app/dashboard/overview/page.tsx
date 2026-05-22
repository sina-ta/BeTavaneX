"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import KpiCard from "@/components/KpiCard";

import RecommendationCard from "@/components/RecommendationCard";

export default function OverviewPage() {

  const [dashboardData, setDashboardData] =
    useState<any>(null);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/dashboard")
      .then((res) => res.json())
      .then((data) => {

        console.log(data);

        setDashboardData(data);
      })
      .catch((err) => {

        console.log(err);
      });

  }, []);

  if (!dashboardData) {

    return (

      <div className="p-10">

        Loading...

      </div>
    );
  }

  return (

    <div className="space-y-8">

      {/* PAGE TITLE */}

      <h1 className="page-title">

        Project Overview

      </h1>

      {/* RECOMMENDATION */}

      {
        dashboardData.tasks?.[0]
          ?.recommendation && (

          <RecommendationCard
            title={
              dashboardData.tasks[0]
                .recommendation.title
            }
            message={
              dashboardData.tasks[0]
                .recommendation.action
            }
          />
        )
      }

      {/* KPI SECTION */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-4
          gap-6
        "
      >

        <KpiCard
          title="Total Work Orders"
          value={
            dashboardData.summary
              .total_work_orders
          }
        />

        <KpiCard
          title="Total Reports"
          value={
            dashboardData.summary
              .total_reports
          }
        />

        <KpiCard
          title="Budget Health"
          value={
            dashboardData.summary
              .avg_cpi
          }
        />

        <KpiCard
          title="Project Speed"
          value={
            dashboardData.summary
              .avg_spi
          }
        />

      </div>

      {/* TASK TABLE */}

      <div className="table-container">

        <div className="p-6">

          <h2 className="section-title">

            Project Tasks

          </h2>

        </div>

        <table className="table-base">

          <thead className="table-head">

            <tr>

              <th className="table-head-cell">
                Task
              </th>

              <th className="table-head-cell">
                Progress
              </th>

              <th className="table-head-cell">
                CPI
              </th>

              <th className="table-head-cell">
                SPI
              </th>

              <th className="table-head-cell">
                Alert
              </th>

            </tr>

          </thead>

          <tbody>

            {dashboardData.tasks.map(
              (task: any) => (

                <tr
                  key={task.task_id}
                  className="table-row"
                >

                  <td className="table-cell">

                    <Link
                      href={`/task/${task.task_id}`}
                      className="
                        text-blue-600
                        font-semibold
                        hover:underline
                      "
                    >

                      {task.task_id}

                    </Link>

                  </td>

                  <td className="table-cell">

                    {
                      Number(
                        task.progress_percent
                      ).toFixed(2)
                    }%

                  </td>

                  <td className="table-cell">

                    {
                      Number(task.cpi)
                        .toFixed(2)
                    }

                  </td>

                  <td className="table-cell">

                    {
                      Number(task.spi)
                        .toFixed(2)
                    }

                  </td>

                  <td className="table-cell">

                    {task.alert}

                  </td>

                </tr>
              )
            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}