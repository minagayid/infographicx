import { useWorkspace } from "../stores/workspace";
import { useAgents } from "../stores/agents";
export default function ProjectDetail() {
  const { mode } = useWorkspace();
  const { agents } = useAgents();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">{mode.toUpperCase()} Workspace</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="border border-gray-800 rounded p-4">
          <h2 className="text-sm text-gray-400 mb-2">Active Agents</h2>
          <div className="space-y-2">
            {agents.map((a) => (
              <div key={a.id} className="flex justify-between text-sm">
                <span>{a.name}</span>
                <span className="text-gray-500">{a.status}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="border border-gray-800 rounded p-4">
          <h2 className="text-sm text-gray-400 mb-2">Knowledge Structure</h2>
          <p className="text-sm text-gray-500">Interactive visualization renders here.</p>
        </div>
      </div>
    </div>
  );
}
