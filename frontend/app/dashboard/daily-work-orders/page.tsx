"use client";

import { useEffect, useState } from "react";

export default function DailyWorkOrdersPage() {

  const [workOrders, setWorkOrders] = useState<any[]>([]);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/daily-work-orders")

      .then((res) => res.json())

      .then((data) => {

        setWorkOrders(data);

      });

  }, []);

  return (

    <div className="space-y-6">

      <h1 className="text-3xl font-bold text-black">

        Daily Work Orders

      </h1>

      <table className="w-full border border-gray-300 bg-white text-black shadow rounded-lg overflow-hidden">

        <thead>

          <tr className="bg-black text-white">

            <th className="p-2">Task</th>

            <th className="p-2">Assigned To</th>

            <th className="p-2">Planned Qty</th>

            <th className="p-2">Unit</th>

            <th className="p-2">Priority</th>

            <th className="p-2">Status</th>

          </tr>

        </thead>

        <tbody>

          {workOrders.map((item: any) => (

            <tr
                key={item.id}
                className="border-b hover:bg-gray-100 transition"
            >

              <td className="p-2">

                {item.task_id}

              </td>

              <td className="p-2">

                {item.assigned_to}

              </td>

              <td className="p-2">

                {item.planned_qty}

              </td>

              <td className="p-2">

                {item.unit}

              </td>

              <td className="p-2">

                {item.priority}

              </td>

              <td className="p-2">

                {item.status}

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  );
}