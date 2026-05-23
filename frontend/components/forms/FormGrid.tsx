type Props = {
  children: React.ReactNode;
};

export default function FormGrid({
  children,
}: Props) {

  return (

    <div
      className="
        grid
        grid-cols-1
        md:grid-cols-2
        gap-6
      "
    >

      {children}

    </div>
  );
}