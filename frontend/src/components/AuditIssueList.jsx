const severityStyles = {
  critical: "bg-red-500/10 border-red-500/30 text-red-400",
  warning: "bg-yellow-500/10 border-yellow-500/30 text-yellow-400",
  info: "bg-blue-500/10 border-blue-500/30 text-blue-400",
};

export default function AuditIssueList({ issues }) {
  const grouped = {};
  issues.forEach((issue) => {
    if (!grouped[issue.issue_type]) grouped[issue.issue_type] = [];
    grouped[issue.issue_type].push(issue);
  });

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([type, items]) => (
        <details key={type} className="bg-gray-900 rounded-lg border border-gray-800">
          <summary className="px-4 py-3 cursor-pointer flex justify-between items-center">
            <span className="font-medium text-sm">
              {type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </span>
            <span className={`text-xs px-2 py-1 rounded border ${severityStyles[items[0].severity]}`}>
              {items.length} {items[0].severity}
            </span>
          </summary>
          <div className="px-4 pb-3 space-y-2">
            {items.map((issue) => (
              <div key={issue.id} className="text-sm border-t border-gray-800 pt-2">
                <p className="text-gray-300">{issue.description}</p>
                {issue.page_url && <p className="text-gray-500 text-xs">{issue.page_url}</p>}
                {issue.fix_suggestion && (
                  <p className="text-green-400/70 text-xs mt-1">Fix: {issue.fix_suggestion}</p>
                )}
              </div>
            ))}
          </div>
        </details>
      ))}
      {issues.length === 0 && (
        <p className="text-gray-500 text-center py-4">No issues found!</p>
      )}
    </div>
  );
}
