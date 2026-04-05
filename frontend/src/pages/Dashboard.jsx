import { useEffect, useState } from "react";
import { fetchDashboard } from "../api/client";
import StoreCard from "../components/StoreCard";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-400">Loading...</div>;
  if (!data) return <div className="text-red-400">Failed to load dashboard</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Total Stores</p>
          <p className="text-3xl font-bold mt-1">{data.total_stores}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Total Pages</p>
          <p className="text-3xl font-bold mt-1">{data.total_pages}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Tracked Keywords</p>
          <p className="text-3xl font-bold mt-1">{data.total_keywords}</p>
        </div>
      </div>

      {/* Store cards */}
      <h3 className="text-lg font-semibold mb-4">Your Stores</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.stores.map((store) => (
          <StoreCard key={store.id} store={store} />
        ))}
      </div>
    </div>
  );
}
