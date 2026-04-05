import { useEffect, useState } from "react";
import { fetchStores, fetchPages, updatePage, generateMeta } from "../api/client";
import MetaEditor from "../components/MetaEditor";

export default function OnPageSEO() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      setLoading(true);
      fetchPages(selectedStore)
        .then((res) => setPages(res.data.results))
        .finally(() => setLoading(false));
    }
  }, [selectedStore]);

  const handleSave = (pageId, data) => {
    updatePage(selectedStore, pageId, data).then(() => {
      setPages((prev) =>
        prev.map((p) => (p.id === pageId ? { ...p, ...data } : p))
      );
    });
  };

  const handleAIGenerate = async (pageId) => {
    const res = await generateMeta(pageId, []);
    return res.data;
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">On-Page SEO</h2>

      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {loading ? (
        <p className="text-gray-400">Loading pages...</p>
      ) : (
        <MetaEditor pages={pages} onSave={handleSave} onAIGenerate={handleAIGenerate} />
      )}
    </div>
  );
}
