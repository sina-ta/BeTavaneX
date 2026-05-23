type Props = {
  children: React.ReactNode;
  head?: boolean;
};

export default function TableCell({
  children,
  head = false,
}: Props) {

  if (head) {

    return (

      <th className="table-head-cell">

        {children}

      </th>
    );
  }

  return (

    <td className="table-cell">

      {children}

    </td>
  );
}