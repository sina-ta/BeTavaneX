type Props = {
  title: string;
};

export default function SubmitButton({
  title,
}: Props) {

  return (

    <button
      type="submit"
      className="
        rounded-2xl
        bg-blue-600
        px-6
        py-4
        font-semibold
        text-white
        transition

        hover:bg-blue-700
      "
    >

      {title}

    </button>
  );
}