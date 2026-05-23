import Link from "next/link";

import StatusBadge from "../StatusBadge";

import TableWrapper from "./TableWrapper";

import TableHead from "./TableHead";

import TableRow from "./TableRow";

import TableCell from "./TableCell";

import EmptyState from "./EmptyState";

type Props = {
  tasks: any[];
};

export default function TasksTable({
  tasks,
}: Props) {

  if (!tasks || tasks.length === 0) {

    return (

      <TableWrapper title="Project Tasks">

        <EmptyState
          title="No tasks found."
        />

      </TableWrapper>
    );
  }

  return (

    <TableWrapper title="Project Tasks">

      <table className="table-base">

        <TableHead>

          <tr>

            <TableCell head>
              Task
            </TableCell>

            <TableCell head>
              Progress
            </TableCell>

            <TableCell head>
              CPI
            </TableCell>

            <TableCell head>
              SPI
            </TableCell>

            <TableCell head>
              Alert
            </TableCell>

          </tr>

        </TableHead>

        <tbody>

          {tasks.map(
            (task: any) => (

              <TableRow
                key={task.task_id}
              >

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

                  {
                    Number(
                      task.progress_percent
                    ).toFixed(2)
                  }%

                </TableCell>

                <TableCell>

                  {
                    Number(task.cpi)
                      .toFixed(2)
                  }

                </TableCell>

                <TableCell>

                  {
                    Number(task.spi)
                      .toFixed(2)
                  }

                </TableCell>

                <TableCell>

                  <StatusBadge
                    status={task.alert}
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