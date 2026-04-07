import { useEffect, useState } from "react";
import {
  fetchStores,
  fetchBacklinkSummary,
  fetchBacklinkSnapshot,
  fetchBacklinks,
  refreshBacklinks,
  fetchProspects,
  createProspect,
  suggestProspects,
  sendProspectEmail,
  updateProspectStatus,
  fetchCampaigns,
} from "../api/client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const STATUS_COLORS = {
  new: "bg-gray-700 text-gray-300",
  emailed: "bg-blue-900 text-blue-300",
  followed_up: "bg-yellow-900 text-yellow-300",
  replied: "bg-purple-900 text-purple-300",
  won: "bg-green-900 text-green-300",
  rejected: "bg-red-900 text-red-300",
};

export default function Backlinks() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const [summary, setSummary] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [backlinks, setBacklinks] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const [prospects, setProspects] = useState([]);
  const [suggesting, setSuggesting] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProspect, setNewProspect] = useState({ website_url: "", contact_email: "" });

  const [campaigns, setCampaigns] = useState([]);
  const [expandedCampaign, setExpandedCampaign] = useState(null);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedStore) return;
    fetchBacklinkSummary(selectedStore).then((res) => setSummary(res.data)).catch(() => {});
    fetchBacklinkSnapshot(selectedStore).then((res) => setSnapshots(res.data)).catch(() => {});
    fetchBacklinks(selectedStore).then((res) => setBacklinks(res.data.results)).catch(() => {});
    fetchProspects(selectedStore).then((res) => setProspects(res.data.results)).catch(() => {});
    fetchCampaigns(selectedStore).then((res) => setCampaigns(res.data.results)).catch(() => {});
  }, [selectedStore]);

  const handleRefresh = () => {
    setRefreshing(true);
    refreshBacklinks(selectedStore)
      .then(() => alert("Backlink refresh queued. Check back in a few minutes."))
      .catch(() => alert("Refresh failed."))
      .finally(() => setRefreshing(false));
  };

  const handleSuggest = () => {
    setSuggesting(true);
    suggestProspects(selectedStore)
      .then(() => alert("Prospect suggestion queued. Check back in a few minutes."))
      .catch(() => alert("Suggestion failed."))
      .finally(() => setSuggesting(false));
  };

  const handleAddProspect = () => {
    if (!newProspect.website_url) return;
    createProspect({ ...newProspect, store: selectedStore, source: "manual" })
      .then((res) => {
        setProspects((prev) => [res.data, ...prev]);
        setNewProspect({ website_url: "", contact_email: "" });
        setShowAddForm(false);
      })
      .catch(() => alert("Failed to add prospect."));
  };

  const handleSendEmail = (prospectId) => {
    setSendingEmail(prospectId);
    sendProspectEmail(prospectId)
      .then((res) => {
        setCampaigns((prev) => [res.data, ...prev]);
        setProspects((prev) =>
          prev.map((p) => p.id === prospectId ? { ...p, status: "emailed" } : p)
        );
        setActiveTab("campaigns");
      })
      .catch((err) => alert(err.response?.data?.error || "Email send failed."))
      .finally(() => setSendingEmail(null));
  };

  const handleStatusChange = (prospectId, newStatus) => {
    updateProspectStatus(prospectId, newStatus)
      .then((res) => {
        setProspects((prev) => prev.map((p) => p.id === prospectId ? res.data : p));
      })
      .catch(() => alert("Status update failed."));
  };

  const chartData = [...snapshots].reverse().map((s) => ({
    date: s.date,
    total: s.total_count,
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Backlinks</h2>
        <select
          value={selectedStore || ""}
          onChange={(e) => setSelectedStore(Number(e.target.value))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
        >
          {stores.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      <div className="flex gap-1 mb-6 border-b border-gray-800">
        {["overview", "prospects", "campaigns"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
              activeTab === tab
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total Backlinks", value: summary?.total ?? "-" },
              { label: "Dofollow %", value: summary ? `${summary.dofollow_pct}%` : "-" },
              { label: "New This Week", value: summary?.new_this_week ?? "-" },
              { label: "Lost This Week", value: summary?.lost_this_week ?? "-" },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <p className="text-gray-400 text-xs mb-1">{label}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
            ))}
          </div>

          <div className="flex justify-end mb-4">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {refreshing ? "Queuing..." : "Refresh Backlinks"}
            </button>
          </div>

          {chartData.length > 0 && (
            <div className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
              <h3 className="font-semibold mb-4">Backlinks Over Time</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: "#1F2937", border: "none" }} />
                  <Line type="monotone" dataKey="total" stroke="#3B82F6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  <th className="text-left px-4 py-2 text-gray-400">Source Domain</th>
                  <th className="text-left px-4 py-2 text-gray-400">Anchor Text</th>
                  <th className="text-left px-4 py-2 text-gray-400">DR</th>
                  <th className="text-left px-4 py-2 text-gray-400">Type</th>
                  <th className="text-left px-4 py-2 text-gray-400">First Seen</th>
                  <th className="text-left px-4 py-2 text-gray-400">Status</th>
                </tr>
              </thead>
              <tbody>
                {backlinks.map((bl) => {
                  let hostname = bl.source_url;
                  try { hostname = new URL(bl.source_url).hostname; } catch {}
                  return (
                    <tr key={bl.id} className="border-t border-gray-800">
                      <td className="px-4 py-2 text-blue-400 text-xs">
                        <a href={bl.source_url} target="_blank" rel="noopener noreferrer">{hostname}</a>
                      </td>
                      <td className="px-4 py-2 text-gray-300 text-xs">{bl.anchor_text || "-"}</td>
                      <td className="px-4 py-2">{bl.domain_rank}</td>
                      <td className="px-4 py-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${bl.is_dofollow ? "bg-green-900 text-green-300" : "bg-gray-700 text-gray-400"}`}>
                          {bl.is_dofollow ? "dofollow" : "nofollow"}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-gray-400 text-xs">{bl.first_seen}</td>
                      <td className="px-4 py-2">
                        {bl.is_lost && <span className="text-xs px-2 py-0.5 rounded-full bg-red-900 text-red-300">lost</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {backlinks.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-8">No backlinks found. Click "Refresh Backlinks" to fetch from DataForSEO.</p>
            )}
          </div>
        </div>
      )}

      {activeTab === "prospects" && (
        <div>
          <div className="flex gap-2 mb-4">
            <button
              onClick={handleSuggest}
              disabled={suggesting}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {suggesting ? "Queuing..." : "Auto-suggest Prospects"}
            </button>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm font-medium"
            >
              Add Manually
            </button>
          </div>

          {showAddForm && (
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 mb-4 flex gap-3">
              <input
                value={newProspect.website_url}
                onChange={(e) => setNewProspect((p) => ({ ...p, website_url: e.target.value }))}
                placeholder="https://example.com"
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              />
              <input
                value={newProspect.contact_email}
                onChange={(e) => setNewProspect((p) => ({ ...p, contact_email: e.target.value }))}
                placeholder="editor@example.com"
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              />
              <button
                onClick={handleAddProspect}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium"
              >
                Add
              </button>
            </div>
          )}

          <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  <th className="text-left px-4 py-2 text-gray-400">Website</th>
                  <th className="text-left px-4 py-2 text-gray-400">DR</th>
                  <th className="text-left px-4 py-2 text-gray-400">Relevance</th>
                  <th className="text-left px-4 py-2 text-gray-400">Status</th>
                  <th className="text-left px-4 py-2 text-gray-400">Source</th>
                  <th className="text-left px-4 py-2 text-gray-400"></th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((p) => (
                  <tr key={p.id} className="border-t border-gray-800">
                    <td className="px-4 py-2 text-blue-400 text-xs">
                      <a href={p.website_url} target="_blank" rel="noopener noreferrer">
                        {p.website_url.replace(/^https?:\/\//, "")}
                      </a>
                    </td>
                    <td className="px-4 py-2">{p.domain_rank}</td>
                    <td className="px-4 py-2">
                      <span className={`font-medium ${p.niche_relevance_score >= 70 ? "text-green-400" : p.niche_relevance_score >= 40 ? "text-yellow-400" : "text-gray-400"}`}>
                        {p.niche_relevance_score}/100
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <select
                        value={p.status}
                        onChange={(e) => handleStatusChange(p.id, e.target.value)}
                        className="text-xs bg-gray-800 border border-gray-700 rounded px-2 py-0.5 cursor-pointer"
                      >
                        {Object.keys(STATUS_COLORS).map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">{p.source}</td>
                    <td className="px-4 py-2">
                      {p.status === "new" && (
                        <button
                          onClick={() => handleSendEmail(p.id)}
                          disabled={sendingEmail === p.id}
                          className="text-blue-400 hover:text-blue-300 text-xs disabled:opacity-50"
                        >
                          {sendingEmail === p.id ? "Sending..." : "Send Email"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {prospects.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-8">No prospects yet. Click "Auto-suggest" or add manually.</p>
            )}
          </div>
        </div>
      )}

      {activeTab === "campaigns" && (
        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-800">
              <tr>
                <th className="text-left px-4 py-2 text-gray-400">Prospect</th>
                <th className="text-left px-4 py-2 text-gray-400">Subject</th>
                <th className="text-left px-4 py-2 text-gray-400">Sent</th>
                <th className="text-left px-4 py-2 text-gray-400">Via</th>
                <th className="text-left px-4 py-2 text-gray-400">Reply</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <>
                  <tr
                    key={c.id}
                    className="border-t border-gray-800 cursor-pointer hover:bg-gray-800"
                    onClick={() => setExpandedCampaign(expandedCampaign === c.id ? null : c.id)}
                  >
                    <td className="px-4 py-2 text-blue-400 text-xs">
                      {c.prospect_url?.replace(/^https?:\/\//, "") || "-"}
                    </td>
                    <td className="px-4 py-2 text-xs">{c.subject}</td>
                    <td className="px-4 py-2 text-gray-400 text-xs">
                      {c.sent_at ? new Date(c.sent_at).toLocaleDateString() : "Failed"}
                    </td>
                    <td className="px-4 py-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${c.sent_via === "gmail" ? "bg-red-900 text-red-300" : "bg-gray-700 text-gray-300"}`}>
                        {c.sent_via}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      {c.reply_received && <span className="text-xs px-2 py-0.5 rounded-full bg-green-900 text-green-300">replied</span>}
                    </td>
                  </tr>
                  {expandedCampaign === c.id && (
                    <tr key={`${c.id}-body`} className="border-t border-gray-800 bg-gray-900">
                      <td colSpan={5} className="px-4 py-3">
                        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans">{c.body}</pre>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
          {campaigns.length === 0 && (
            <p className="text-gray-500 text-sm text-center py-8">No campaigns yet. Send outreach emails from the Prospects tab.</p>
          )}
        </div>
      )}
    </div>
  );
}
