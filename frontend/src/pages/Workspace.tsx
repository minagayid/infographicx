import { useWorkspace } from "../stores/workspace";
import { Upload, FileText, GitBranch, Globe, Video, Database } from "lucide-react";

const SUGGESTIONS = [
  { label: "Paper", icon: FileText, mode: "paper" as const },
  { label: "Repository", icon: GitBranch, mode: "code" as const },
  { label: "Website", icon: Globe, mode: "dashboard" as const },
  { label: "Video", icon: Video, mode: "whiteboard" as const },
  { label: "Dataset", icon: Database, mode: "flow" as const },
];

export default function Workspace() {
  const { mode, setMode } = useWorkspace();

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">InfographicX</h1>
          <p className="text-sm text-gray-500">The AI Operating System for Visual Knowledge</p>
        </div>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as any)}
          className="bg-gray-900 border border-gray-800 rounded px-2 py-1 text-xs"
        >
          <option value="paper">Research Mode</option>
          <option value="code">Repository Mode</option>
          <option value="dashboard">Dashboard Mode</option>
          <option value="flow">Graph Mode</option>
        </select>
      </div>
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-3 gap-4">
          {SUGGESTIONS.map((s) => (
            <div
              key={s.label}
              onClick={() => setMode(s.mode)}
              className="border border-gray-800 rounded-lg p-4 hover:border-indigo-500/50 cursor-pointer"
            >
              <s.icon className="w-5 h-5 text-indigo-400" />
              <p className="mt-2 text-sm">{s.label}</p>
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-500 mt-8">Drag and drop any file, URL, or repository to start.</p>
      </div>
    </div>
  );
}
