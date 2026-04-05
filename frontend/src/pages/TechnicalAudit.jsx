import { useEffect, useState } from "react";
import { fetchStores, triggerAudit, fetchAuditRuns } from "../api/client";
import AuditIssueList from "../components/AuditIssueList";

export default function TechnicalAudit() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [auditRuns, setAuditRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchAuditRuns(selectedStore).then((res) => {
        setAuditRuns(res.data.results);
        if (res.data.results.length > 0) setSelectedRun(res.data.results[0]);
      });
    }
  }, [selectedStore]);

  const handleTrigger = () => {
    triggerAudit(selectedStore).then(() => alert("Audit started! Refresh in a moment."));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Technical SEO Audit</h2>
        <button
          onClick={handleTrigger}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium"
        >
          Run Audit
        </button>
      </div>

      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {selectedRun && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Status</p>
              <p className="font-medium capitalize">{selectedRun.status}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Critical</p>
              <p className="text-2xl font-bold text-red-400">{selectedRun.issue_summary?.critical || 0}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Warnings</p>
              <p className="text-2xl font-bold text-yellow-400">{selectedRun.issue_summary?.warning || 0}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Info</p>
              <p className="text-2xl font-bold text-blue-400">{selectedRun.issue_summary?.info || 0}</p>
            </div>
          </div>

          <AuditIssueList issues={selectedRun.issues || []} />
        </>
      )}

      {!selectedRun && (
        <p className="text-gray-500 text-center py-8">No audits run yet. Click "Run Audit" to start.</p>
      )}
    </div>
  );
}
