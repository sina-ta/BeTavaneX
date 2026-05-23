type Props = {
  children: React.ReactNode;
};

export default function TableRow({
  children,
}: Props) {

  return (

    <tr className="table-row">

      {children}

    </tr>
  );
}