"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import PageHeader from "@/components/ui/PageHeader";

import SectionCard from "@/components/ui/SectionCard";

import Badge from "@/components/ui/Badge";

export default function DailyWorkOrdersPage() {

  const [workOrders, setWorkOrders] =
    useState<any[]>([]);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/daily-work-orders")

      .then((res) => res.json())

      .then((data) => {

        setWorkOrders(data);

      })

      .catch((err) => {

        console.log(err);

      });

  }, []);

  return (

    <div className="page-wrapper">

      <PageHeader
        title="Daily Work Orders"
        subtitle="
          Track all active
          construction tasks
        "
      />

      <SectionCard
        title="Active Work Orders"
      >

        <table className="table-base">

          <thead className="table-head">

            <tr>

              <th className="table-head-cell">
                Task
              </th>

              <th className="table-head-cell">
                Assigned To
              </th>

              <th className="table-head-cell">
                Planned Qty
              </th>

              <th className="table-head-cell">
                Unit
              </th>

              <th className="table-head-cell">
                Priority
              </th>

              <th className="table-head-cell">
                Status
              </th>

            </tr>

          </thead>

          <tbody>

            {workOrders.map((item: any) => (

              <tr
                key={item.id}
                className="table-row"
              >

                <td className="table-cell">

                  <Link
                    href={`/task/${item.task_id}`}
                    className="
                      text-blue-400
                      font-semibold
                      hover:underline
                    "
                  >

                    {item.task_id}

                  </Link>

                </td>

                <td className="table-cell">

                  {item.assigned_to}

                </td>

                <td className="table-cell">

                  {item.planned_qty}

                </td>

                <td className="table-cell">

                  {item.unit}

                </td>

                <td className="table-cell">

                  <Badge
                    status={item.priority}
                  />

                </td>

                <td className="table-cell">

                  <Badge
                    status={item.status}
                  />

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </SectionCard>

    </div>

  );
}