import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchStoreDashboard } from "../api/client";
import SEOScoreBadge from "../components/SEOScoreBadge";

export default function StoreDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchStoreDashboard(id).then((res) => setData(res.data));
  }, [id]);

  if (!data) return <div className="text-gray-400">Loading...</div>;

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <SEOScoreBadge score={data.store.seo_score} />
        <div>
          <h2 className="text-2xl font-bold">{data.store.name}</h2>
          <p className="text-gray-400">{data.store.shopify_url}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Pages</p>
          <p className="text-2xl font-bold">{data.pages_count}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Tracked Keywords</p>
          <p className="text-2xl font-bold">{data.keywords_count}</p>
        </div>
      </div>

      {/* Top Keywords */}
      <h3 className="text-lg font-semibold mb-3">Top Keywords</h3>
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden mb-8">
        <table className="w-full text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="text-left px-4 py-2 text-gray-400">Keyword</th>
              <th className="text-left px-4 py-2 text-gray-400">Volume</th>
              <th className="text-left px-4 py-2 text-gray-400">Position</th>
            </tr>
          </thead>
          <tbody>
            {data.top_keywords.map((kw, i) => (
              <tr key={i} className="border-t border-gray-800">
                <td className="px-4 py-2">{kw.keyword}</td>
                <td className="px-4 py-2">{kw.search_volume}</td>
                <td className="px-4 py-2">
                  {kw.position ? `#${kw.position}` : "Not ranked"}
                </td>
              </tr>
            ))}
            {data.top_keywords.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-4 text-gray-500 text-center">No keywords tracked yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Recent Audit */}
      <h3 className="text-lg font-semibold mb-3">Latest Audit</h3>
      {data.recent_audit ? (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Status</p>
              <p className="font-medium capitalize">{data.recent_audit.status}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Pages Crawled</p>
              <p className="font-medium">{data.recent_audit.pages_crawled}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Critical</p>
              <p className="font-medium text-red-400">{data.recent_audit.critical}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Warnings</p>
              <p className="font-medium text-yellow-400">{data.recent_audit.warnings}</p>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-500">No audits run yet</p>
      )}
    </div>
  );
}
