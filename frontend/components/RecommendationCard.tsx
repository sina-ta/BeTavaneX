type Props = {
  title: string;
  message: string;
};

export default function RecommendationCard({
  title,
  message,
}: Props) {

  return (

    <div className="section-card">

      <div
        className="
          flex
          items-start
          gap-4
        "
      >

        <div className="text-2xl">
          ⚡
        </div>

        <div>

          <div
            className="
              text-2xl
              font-bold
              text-white
              mb-2
            "
          >
            {title}
          </div>

          <div
            className="
              text-gray-400
              text-lg
            "
          >
            {message}
          </div>

        </div>

      </div>

    </div>
  );
}