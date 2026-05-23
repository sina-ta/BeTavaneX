type Props = {
  title?: string;
  children: React.ReactNode;
};

export default function FormLayout({
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

      <div className="space-y-6">

        {children}

      </div>

    </div>
  );
}