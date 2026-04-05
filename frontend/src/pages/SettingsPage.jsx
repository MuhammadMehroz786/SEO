export default function SettingsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Settings</h2>
      <div className="bg-gray-900 rounded-lg p-5 border border-gray-800">
        <p className="text-gray-400">
          API keys and scheduling are configured via environment variables on the server.
          See <code className="text-blue-400">.env.example</code> for required keys.
        </p>
        <div className="mt-4 space-y-2 text-sm">
          <p className="text-gray-300">Required API Keys:</p>
          <ul className="list-disc list-inside text-gray-400 space-y-1">
            <li>ANTHROPIC_API_KEY — Claude AI for content generation</li>
            <li>SERPAPI_KEY — Rank tracking</li>
            <li>DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD — Keyword research</li>
            <li>Shopify access tokens — Per-store (added in Stores page)</li>
          </ul>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          <p className="text-gray-300">Automated Schedule:</p>
          <ul className="list-disc list-inside text-gray-400 space-y-1">
            <li>2:00 AM — Sync all stores from Shopify</li>
            <li>4:00 AM — Track keyword rankings</li>
            <li>6:00 AM — Recalculate SEO scores</li>
            <li>Sunday 3:00 AM — Full site audit</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
