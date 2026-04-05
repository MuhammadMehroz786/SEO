import { Link } from "react-router-dom";
import SEOScoreBadge from "./SEOScoreBadge";

export default function StoreCard({ store }) {
  return (
    <Link
      to={`/stores/${store.id}`}
      className="bg-gray-900 rounded-lg p-5 border border-gray-800 hover:border-gray-600 transition-colors"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-white">{store.name}</h4>
          <p className="text-sm text-gray-400">{store.shopify_url}</p>
        </div>
        <SEOScoreBadge score={store.seo_score} />
      </div>
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div>
          <p className="text-gray-500">Pages</p>
          <p className="font-medium">{store.pages_count}</p>
        </div>
        <div>
          <p className="text-gray-500">Keywords</p>
          <p className="font-medium">{store.keywords_count}</p>
        </div>
        <div>
          <p className="text-gray-500">Issues</p>
          <p className="font-medium">{store.issues_count}</p>
        </div>
      </div>
    </Link>
  );
}
