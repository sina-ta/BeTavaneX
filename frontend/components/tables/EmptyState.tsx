type Props = {
  title: string;
};

export default function EmptyState({
  title,
}: Props) {

  return (

    <div
      className="
        flex
        items-center
        justify-center
        py-16
        text-gray-500
      "
    >

      {title}

    </div>
  );
}