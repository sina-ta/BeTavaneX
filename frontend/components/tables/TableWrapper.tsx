type Props = {
  title?: string;
  children: React.ReactNode;
};

export default function TableWrapper({
  title,
  children,
}: Props) {

  return (

    <div className="section-card">

      {title && (

        <h2 className="section-title">

          {title}

        </h2>

      )}

      <div className="overflow-x-auto">

        {children}

      </div>

    </div>
  );
}