type RecommendationCardProps = {

  title: string;

  message: string;
};

export default function RecommendationCard({

  title,
  message,

}: RecommendationCardProps) {

  return (

    <div className="
      bg-white
      rounded-2xl
      shadow
      p-6
      border-l-4
      border-blue-500
    ">

      <h2 className="
        text-xl
        font-bold
        text-gray-800
        mb-2
      ">
        ⚡ {title}
      </h2>

      <p className="
        text-gray-600
        leading-relaxed
      ">
        {message}
      </p>

    </div>
  );
}