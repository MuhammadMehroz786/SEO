export default function SEOScoreBadge({ score }) {
  const color =
    score >= 80
      ? "text-green-400 border-green-400/30 bg-green-400/10"
      : score >= 50
        ? "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
        : "text-red-400 border-red-400/30 bg-red-400/10";

  return (
    <div className={`rounded-full w-12 h-12 flex items-center justify-center border text-sm font-bold ${color}`}>
      {score}
    </div>
  );
}
