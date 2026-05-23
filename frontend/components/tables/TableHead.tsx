type Props = {
  children: React.ReactNode;
};

export default function TableHead({
  children,
}: Props) {

  return (

    <thead className="table-head">

      {children}

    </thead>
  );
}