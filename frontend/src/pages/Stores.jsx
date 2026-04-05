import { useEffect, useState } from "react";
import { fetchStores, createStore, deleteStore, syncStore } from "../api/client";
import StoreCard from "../components/StoreCard";

export default function Stores() {
  const [stores, setStores] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", shopify_url: "", access_token: "" });

  const load = () => {
    fetchStores().then((res) => setStores(res.data.results));
  };

  useEffect(load, []);

  const handleCreate = (e) => {
    e.preventDefault();
    createStore(form).then(() => {
      setShowForm(false);
      setForm({ name: "", shopify_url: "", access_token: "" });
      load();
    });
  };

  const handleSync = (id) => {
    syncStore(id).then(() => alert("Sync started!"));
  };

  const handleDelete = (id) => {
    if (confirm("Delete this store?")) {
      deleteStore(id).then(load);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Stores</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Add Store
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
          <div className="grid grid-cols-3 gap-4">
            <input
              placeholder="Store Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              required
            />
            <input
              placeholder="store-name.myshopify.com"
              value={form.shopify_url}
              onChange={(e) => setForm({ ...form, shopify_url: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              required
            />
            <input
              placeholder="Access Token (shpat_...)"
              value={form.access_token}
              onChange={(e) => setForm({ ...form, access_token: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              type="password"
              required
            />
          </div>
          <button type="submit" className="mt-3 bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-medium">
            Save Store
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stores.map((store) => (
          <div key={store.id} className="relative">
            <StoreCard store={store} />
            <div className="absolute top-3 right-3 flex gap-2">
              <button
                onClick={(e) => { e.preventDefault(); handleSync(store.id); }}
                className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-600/30"
              >
                Sync
              </button>
              <button
                onClick={(e) => { e.preventDefault(); handleDelete(store.id); }}
                className="text-xs bg-red-600/20 text-red-400 px-2 py-1 rounded hover:bg-red-600/30"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
