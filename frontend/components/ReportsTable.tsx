export default function ReportsTable({
  reports,
}: any) {

  return (

    <div className="table-container">

      <h2 className="table-title">

        Daily Reports

      </h2>

      <table className="table-base">

        <thead className="table-head">

          <tr>

            <th className="table-head-cell">
              Reporter
            </th>

            <th className="table-head-cell">
              Qty
            </th>

            <th className="table-head-cell">
              Manpower
            </th>

            <th className="table-head-cell">
              Delay
            </th>

            <th className="table-head-cell">
              Weather
            </th>

          </tr>

        </thead>

        <tbody>

          {reports.map((report: any) => (

            <tr
              key={report.id}
              className="table-row"
            >

              <td className="table-cell">
                {report.reported_by}
              </td>

              <td className="table-cell">
                {report.actual_qty}
              </td>

              <td className="table-cell">
                {report.manpower_count}
              </td>

              <td className="table-cell">
                {report.delay_reason}
              </td>

              <td className="table-cell">
                {report.weather_status}
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}