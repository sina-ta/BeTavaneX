import Link from "next/link";

import StatusBadge from "@/components/ui/StatusBadge";
import SeverityBadge from "@/components/ui/SeverityBadge";
import ProgressBar from "@/components/ui/ProgressBar";
import { resolveSeverity } from "@/lib/operational/severity";

import DenseTableWrapper from "@/components/layout/primitives/DenseTableWrapper";
import TableHead from "./TableHead";
import TableRow from "./TableRow";
import TableCell from "./TableCell";
import EmptyState from "./EmptyState";

import type { WorkforceWorker } from "@/types/workforce";

type Props = {
  workers: WorkforceWorker[];
};

function averageScore(worker: WorkforceWorker): number {
  const values = Object.values(worker.scores).filter(
    (value): value is number =>
      typeof value === "number"
  );

  if (values.length === 0) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export default function WorkforceTable({ workers }: Props) {
  if (!workers || workers.length === 0) {
    return (
      <DenseTableWrapper>
        <EmptyState title="No workforce records found." />
      </DenseTableWrapper>
    );
  }

  return (
    <DenseTableWrapper>
      <table className="table-base">
        <TableHead>
          <tr>
            <TableCell head>Worker</TableCell>
            <TableCell head>Trade</TableCell>
            <TableCell head>Crew</TableCell>
            <TableCell head>Readiness</TableCell>
            <TableCell head>Operational Score</TableCell>
            <TableCell head>Availability</TableCell>
          </tr>
        </TableHead>

        <tbody>
          {workers.map((worker) => {
            const score = averageScore(worker);
            const severity = resolveSeverity(
              worker.availability_status === "available"
                ? score >= 80
                  ? "healthy"
                  : score >= 60
                    ? "warning"
                    : "critical"
                : worker.availability_status
            );

            return (
              <TableRow key={worker.id}>
                <TableCell>
                  <Link
                    href={`/dashboard/workforce/${worker.id}`}
                    className="
                      text-blue-400
                      font-semibold
                      hover:underline
                    "
                  >
                    {worker.full_name}
                  </Link>
                  <div className="text-xs text-gray-500">
                    {worker.current_role ?? "Field Worker"}
                  </div>
                </TableCell>

                <TableCell>{worker.trade}</TableCell>

                <TableCell>{worker.crew ?? "-"}</TableCell>

                <TableCell>
                  <SeverityBadge
                    severity={worker.assignment_readiness}
                  />
                </TableCell>

                <TableCell>
                  <ProgressBar
                    value={score}
                    severity={severity}
                  />
                </TableCell>

                <TableCell>
                  <StatusBadge
                    status={worker.availability_status}
                  />
                </TableCell>
              </TableRow>
            );
          })}
        </tbody>
      </table>
    </DenseTableWrapper>
  );
}
