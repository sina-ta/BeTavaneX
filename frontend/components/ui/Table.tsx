type TableColumn = {

  key: string;
  title: string;

};

type TableProps = {

  columns: TableColumn[];

  data: any[];

};

export default function Table({
  columns,
  data,
}: TableProps) {

  return (

    <div className="table-container">

      <table className="table-base">

        <thead className="table-head">

          <tr>

            {columns.map((column) => (

              <th
                key={column.key}
                className="table-head-cell"
              >
                {column.title}
              </th>

            ))}

          </tr>

        </thead>

        <tbody>

          {data.map((row, index) => (

            <tr
              key={index}
              className="table-row"
            >

              {columns.map((column) => (

                <td
                  key={column.key}
                  className="table-cell"
                >

                  {row[column.key]}

                </td>

              ))}

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  );
}