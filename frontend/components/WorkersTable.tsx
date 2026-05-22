import StatusBadge from "./StatusBadge";

import Link from "next/link";

export default function WorkersTable({
  workers,
}: any) {

  return (

    <div className="table-container">

      <table className="table-base">

        <thead className="table-head">

          <tr>

            <th className="table-head-cell">
              Worker
            </th>

            <th className="table-head-cell">
              Role
            </th>

            <th className="table-head-cell">
              Crew
            </th>

            <th className="table-head-cell">
              Daily Wage
            </th>

            <th className="table-head-cell">
              Score
            </th>

            <th className="table-head-cell">
              Status
            </th>

          </tr>

        </thead>

        <tbody>

          {workers.map((worker: any) => (

            <tr
              key={worker.id}
              className="table-row"
            >

              <td className="table-cell">

                <Link
                  href={`/hr/workers/${worker.id}`}
                  className="
                    text-blue-400
                    font-semibold
                    hover:underline
                  "
                >
                  {worker.full_name}
                </Link>

              </td>

              <td className="table-cell">
                {worker.role}
              </td>

              <td className="table-cell">
                {worker.crew}
              </td>

              <td className="table-cell">
                {worker.daily_wage}
              </td>

              <td className="table-cell">
                {worker.score}
              </td>

              <td className="table-cell">

                <StatusBadge
                  status={worker.status}
                />

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}