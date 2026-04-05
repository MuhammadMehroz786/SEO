import { useState } from "react";

function titleColor(title) {
  if (!title) return "border-red-500/50 bg-red-500/5";
  if (title.length > 60) return "border-yellow-500/50 bg-yellow-500/5";
  if (title.length < 20) return "border-yellow-500/50 bg-yellow-500/5";
  return "border-green-500/50 bg-green-500/5";
}

function descColor(desc) {
  if (!desc) return "border-red-500/50 bg-red-500/5";
  if (desc.length > 160) return "border-yellow-500/50 bg-yellow-500/5";
  if (desc.length < 50) return "border-yellow-500/50 bg-yellow-500/5";
  return "border-green-500/50 bg-green-500/5";
}

export default function MetaEditor({ pages, onSave, onAIGenerate }) {
  const [editing, setEditing] = useState({});
  const [generating, setGenerating] = useState({});

  const startEdit = (page) => {
    setEditing((prev) => ({
      ...prev,
      [page.id]: { title: page.title, meta_description: page.meta_description },
    }));
  };

  const handleGenerate = async (pageId) => {
    setGenerating((prev) => ({ ...prev, [pageId]: true }));
    try {
      const result = await onAIGenerate(pageId);
      setEditing((prev) => ({
        ...prev,
        [pageId]: { title: result.title, meta_description: result.description },
      }));
    } finally {
      setGenerating((prev) => ({ ...prev, [pageId]: false }));
    }
  };

  const handleSave = (pageId) => {
    onSave(pageId, editing[pageId]);
    setEditing((prev) => {
      const next = { ...prev };
      delete next[pageId];
      return next;
    });
  };

  return (
    <div className="space-y-3">
      {pages.map((page) => (
        <div key={page.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-xs text-gray-500 uppercase">{page.page_type}</span>
              <p className="text-sm text-gray-400">{page.url}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleGenerate(page.id)}
                disabled={generating[page.id]}
                className="text-xs bg-purple-600/20 text-purple-400 px-2 py-1 rounded hover:bg-purple-600/30 disabled:opacity-50"
              >
                {generating[page.id] ? "Generating..." : "AI Generate"}
              </button>
              {!editing[page.id] && (
                <button
                  onClick={() => startEdit(page)}
                  className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-600/30"
                >
                  Edit
                </button>
              )}
            </div>
          </div>

          {editing[page.id] ? (
            <div className="space-y-2">
              <div>
                <label className="text-xs text-gray-500">Title ({editing[page.id].title.length}/60)</label>
                <input
                  value={editing[page.id].title}
                  onChange={(e) =>
                    setEditing((prev) => ({
                      ...prev,
                      [page.id]: { ...prev[page.id], title: e.target.value },
                    }))
                  }
                  className={`w-full border rounded px-3 py-2 text-sm bg-transparent ${titleColor(editing[page.id].title)}`}
                />
              </div>
              <div>
                <label className="text-xs text-gray-500">
                  Meta Description ({editing[page.id].meta_description.length}/160)
                </label>
                <textarea
                  value={editing[page.id].meta_description}
                  onChange={(e) =>
                    setEditing((prev) => ({
                      ...prev,
                      [page.id]: { ...prev[page.id], meta_description: e.target.value },
                    }))
                  }
                  rows={2}
                  className={`w-full border rounded px-3 py-2 text-sm bg-transparent ${descColor(editing[page.id].meta_description)}`}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleSave(page.id)}
                  className="text-xs bg-green-600 hover:bg-green-700 px-3 py-1 rounded font-medium"
                >
                  Save
                </button>
                <button
                  onClick={() =>
                    setEditing((prev) => {
                      const next = { ...prev };
                      delete next[page.id];
                      return next;
                    })
                  }
                  className="text-xs text-gray-400 hover:text-white px-3 py-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p className={`text-sm px-2 py-1 rounded border mb-1 ${titleColor(page.title)}`}>
                {page.title || <span className="text-red-400 italic">Missing title</span>}
              </p>
              <p className={`text-sm px-2 py-1 rounded border ${descColor(page.meta_description)}`}>
                {page.meta_description || <span className="text-red-400 italic">Missing description</span>}
              </p>
            </div>
          )}
        </div>
      ))}
      {pages.length === 0 && (
        <p className="text-gray-500 text-center py-8">No pages found. Sync your store first.</p>
      )}
    </div>
  );
}
