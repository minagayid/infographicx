export default function CollaborationPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Collaboration</h1>
      <div className="grid grid-cols-1 gap-2">
        {["Researcher", "Engineer", "Manager", "Designer"].map((r) => (
          <div key={r} className="border border-gray-800 rounded p-3 text-sm">{r}</div>
        ))}
      </div>
    </div>
  );
}
