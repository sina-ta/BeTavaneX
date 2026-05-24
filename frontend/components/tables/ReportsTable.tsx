import TableWrapper from "./TableWrapper";

import TableHead from "./TableHead";

import TableRow from "./TableRow";

import TableCell from "./TableCell";

import EmptyState from "./EmptyState";

import type { DailyReport } from "@/types/report";

type Props = {
  reports: DailyReport[];
};

export default function ReportsTable({
  reports,
}: Props) {

  if (!reports || reports.length === 0) {

    return (

      <TableWrapper title="Daily Reports">

        <EmptyState
          title="No reports found."
        />

      </TableWrapper>
    );
  }

  return (

    <TableWrapper title="Daily Reports">

      <table className="table-base">

        <TableHead>

          <tr>

            <TableCell head>
              Reporter
            </TableCell>

            <TableCell head>
              Qty
            </TableCell>

            <TableCell head>
              Manpower
            </TableCell>

            <TableCell head>
              Delay
            </TableCell>

            <TableCell head>
              Weather
            </TableCell>

          </tr>

        </TableHead>

        <tbody>

          {reports.map((report) => (

              <TableRow
                key={report.id}
              >

                <TableCell>
                  {report.reported_by}
                </TableCell>

                <TableCell>
                  {report.actual_qty}
                </TableCell>

                <TableCell>
                  {report.manpower_count}
                </TableCell>

                <TableCell>
                  {report.delay_reason}
                </TableCell>

                <TableCell>
                  {report.weather_status}
                </TableCell>

              </TableRow>

            )
          )}

        </tbody>

      </table>

    </TableWrapper>
  );
}