export default function ExportPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Export</h1>
      <div className="grid grid-cols-3 gap-3">
        {["HTML", "PDF", "PNG", "SVG", "PPTX", "Website"].map((f) => (
          <button key={f} className="border border-gray-800 rounded p-3 text-sm hover:border-indigo-500/50">
            {f}
          </button>
        ))}
      </div>
    </div>
  );
}
