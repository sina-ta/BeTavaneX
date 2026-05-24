"use client";

import Link from "next/link";

import ProgressBar from "@/components/ui/ProgressBar";
import StatusBadge from "@/components/ui/StatusBadge";
import TaskRecommendationCell from "@/components/tasks/TaskRecommendationCell";
import { alertToSeverity } from "@/lib/operational/kpiMetrics";

import DenseTableWrapper from "@/components/layout/primitives/DenseTableWrapper";
import TableHead from "./TableHead";
import TableRow from "./TableRow";
import TableCell from "./TableCell";
import EmptyState from "./EmptyState";

import type { DashboardTask } from "@/types/dashboard";

type Props = {
  tasks: DashboardTask[];
};

export default function TasksTable({
  tasks,
}: Props) {
  if (!tasks || tasks.length === 0) {
    return (
      <DenseTableWrapper>
        <EmptyState title="No tasks found." />
      </DenseTableWrapper>
    );
  }

  return (
    <DenseTableWrapper>
      <table className="table-base">
        <TableHead>
          <tr>
            <TableCell head>Task</TableCell>
            <TableCell head>Progress</TableCell>
            <TableCell head>CPI</TableCell>
            <TableCell head>SPI</TableCell>
            <TableCell head>Status</TableCell>
            <TableCell head>Recommendation</TableCell>
          </tr>
        </TableHead>

        <tbody>
          {tasks.map((task) => {
            const progressSeverity = alertToSeverity(
              task.alert
            );

            return (
              <TableRow key={task.task_id}>
                <TableCell>
                  <Link
                    href={`/task/${task.task_id}`}
                    className="
                      text-blue-400
                      font-semibold
                      hover:underline
                    "
                  >
                    {task.task_id}
                  </Link>
                </TableCell>

                <TableCell>
                  <ProgressBar
                    value={Number(task.progress_percent)}
                    severity={progressSeverity}
                  />
                </TableCell>

                <TableCell>
                  {Number(task.cpi).toFixed(2)}
                </TableCell>

                <TableCell>
                  {Number(task.spi).toFixed(2)}
                </TableCell>

                <TableCell>
                  <StatusBadge status={task.alert} />
                </TableCell>

                <TableCell>
                  <TaskRecommendationCell
                    recommendation={task.recommendation}
                    alert={task.alert}
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
