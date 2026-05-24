import Link from "next/link";

import StatusBadge from "@/components/ui/StatusBadge";

import TableWrapper from "./TableWrapper";

import TableHead from "./TableHead";

import TableRow from "./TableRow";

import TableCell from "./TableCell";

import EmptyState from "./EmptyState";

import type { Worker } from "@/types/worker";

type Props = {
  workers: Worker[];
};

export default function WorkersTable({
  workers,
}: Props) {

  if (!workers || workers.length === 0) {

    return (

      <TableWrapper title="Workers">

        <EmptyState
          title="No workers found."
        />

      </TableWrapper>
    );
  }

  return (

    <TableWrapper title="Workers">

      <table className="table-base">

        <TableHead>

          <tr>

            <TableCell head>
              Worker
            </TableCell>

            <TableCell head>
              Role
            </TableCell>

            <TableCell head>
              Crew
            </TableCell>

            <TableCell head>
              Daily Wage
            </TableCell>

            <TableCell head>
              Score
            </TableCell>

            <TableCell head>
              Status
            </TableCell>

          </tr>

        </TableHead>

        <tbody>

          {workers.map((worker) => (

              <TableRow
                key={worker.id}
              >

                <TableCell>

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

                </TableCell>

                <TableCell>
                  {worker.role}
                </TableCell>

                <TableCell>
                  {worker.crew}
                </TableCell>

                <TableCell>
                  {worker.daily_wage}
                </TableCell>

                <TableCell>
                  {worker.score}
                </TableCell>

                <TableCell>

                  <StatusBadge
                    status={worker.status}
                  />

                </TableCell>

              </TableRow>

            )
          )}

        </tbody>

      </table>

    </TableWrapper>
  );
}