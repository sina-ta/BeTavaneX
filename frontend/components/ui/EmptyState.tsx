type EmptyStateProps = {

  title: string;

};

export default function EmptyState({
  title,
}: EmptyStateProps) {

  return (

    <div className="empty-state">

      <div className="empty-icon">

        ☐

      </div>

      <p>

        {title}

      </p>

    </div>
  );
}