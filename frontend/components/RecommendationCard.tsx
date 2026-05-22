export default function RecommendationCard({
  title,
  message,
}: any) {

  return (

    <div className="card-base border-l-4 border-blue-500">

      <div className="text-xl font-bold mb-3">

        ⚡ {title}

      </div>

      <div className="text-gray-400">

        {message}

      </div>

    </div>
  );
}