import { useEffect, useState } from "react";
import {
  fetchStores,
  fetchKeywords,
  createKeyword,
  researchKeywords,
  fetchRankHistory,
} from "../api/client";
import RankChart from "../components/RankChart";

export default function Keywords() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [keywords, setKeywords] = useState([]);
  const [researchResults, setResearchResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [searching, setSearching] = useState(false);
  const [selectedKw, setSelectedKw] = useState(null);
  const [rankHistory, setRankHistory] = useState([]);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchKeywords(selectedStore).then((res) => setKeywords(res.data.results));
    }
  }, [selectedStore]);

  const handleResearch = () => {
    setSearching(true);
    researchKeywords(searchTerm)
      .then((res) => setResearchResults(res.data))
      .finally(() => setSearching(false));
  };

  const handleTrack = (kw) => {
    createKeyword({
      store: selectedStore,
      keyword: kw.keyword,
      search_volume: kw.search_volume,
      difficulty: kw.difficulty,
      cpc: kw.cpc || 0,
    }).then(() => fetchKeywords(selectedStore).then((res) => setKeywords(res.data.results)));
  };

  const handleViewHistory = (kwId) => {
    setSelectedKw(kwId);
    fetchRankHistory(kwId).then((res) => setRankHistory(res.data));
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Keyword Research & Tracking</h2>

      {/* Store selector */}
      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {/* Research */}
      <div className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
        <h3 className="font-semibold mb-3">Keyword Research</h3>
        <div className="flex gap-2">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter seed keyword..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleResearch()}
          />
          <button
            onClick={handleResearch}
            disabled={searching}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
          >
            {searching ? "Searching..." : "Research"}
          </button>
        </div>
        {researchResults.length > 0 && (
          <table className="w-full text-sm mt-4">
            <thead>
              <tr className="text-gray-400 text-left">
                <th className="py-2">Keyword</th>
                <th className="py-2">Volume</th>
                <th className="py-2">Difficulty</th>
                <th className="py-2">CPC</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {researchResults.map((kw, i) => (
                <tr key={i} className="border-t border-gray-800">
                  <td className="py-2">{kw.keyword}</td>
                  <td className="py-2">{kw.search_volume}</td>
                  <td className="py-2">{kw.difficulty}</td>
                  <td className="py-2">${kw.cpc || 0}</td>
                  <td className="py-2">
                    <button
                      onClick={() => handleTrack(kw)}
                      className="text-blue-400 hover:text-blue-300 text-xs"
                    >
                      Track
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Tracked Keywords */}
      <h3 className="font-semibold mb-3">Tracked Keywords</h3>
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="text-left px-4 py-2 text-gray-400">Keyword</th>
              <th className="text-left px-4 py-2 text-gray-400">Volume</th>
              <th className="text-left px-4 py-2 text-gray-400">Difficulty</th>
              <th className="text-left px-4 py-2 text-gray-400">Position</th>
              <th className="text-left px-4 py-2 text-gray-400"></th>
            </tr>
          </thead>
          <tbody>
            {keywords.map((kw) => (
              <tr key={kw.id} className="border-t border-gray-800">
                <td className="px-4 py-2">{kw.keyword}</td>
                <td className="px-4 py-2">{kw.search_volume}</td>
                <td className="px-4 py-2">{kw.difficulty}</td>
                <td className="px-4 py-2">
                  {kw.latest_position ? `#${kw.latest_position}` : "-"}
                </td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => handleViewHistory(kw.id)}
                    className="text-blue-400 hover:text-blue-300 text-xs"
                  >
                    History
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Rank History Chart */}
      {selectedKw && rankHistory.length > 0 && (
        <div className="mt-6">
          <RankChart data={rankHistory} />
        </div>
      )}
    </div>
  );
}
