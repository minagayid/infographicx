import {
  LayoutDashboard,
  FileText,
  GitBranch,
  Users,
  Settings,
  Play,
  Share2,
} from "lucide-react";
import { useWorkspace } from "../../stores/workspace";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", mode: "dashboard" as const },
  { icon: FileText, label: "Research", mode: "paper" as const },
  { icon: GitBranch, label: "Repositories", mode: "code" as const },
  { icon: Users, label: "Collaboration", mode: "flow" as const },
  { icon: Share2, label: "Publishing", mode: "paper" as const },
];

export default function Sidebar() {
  const { mode, setMode, sidebarOpen } = useWorkspace();
  if (!sidebarOpen) return null;
  return (
    <aside className="w-52 border-r border-gray-800 flex flex-col">
      <div className="p-3 border-b border-gray-800 text-xs text-gray-500 font-medium">NAVIGATION</div>
      <nav className="flex-1 p-2 space-y-1">
        {NAV.map(({ icon: Icon, ...item }) => (
          <button
            key={item.label}
            onClick={() => setMode(item.mode)}
            className={`
              w-full flex items-center gap-2 px-3 py-2 rounded text-sm
              ${mode === item.mode ? "bg-indigo-500/20 text-indigo-300" : "text-gray-400 hover:bg-gray-900"}
            `}
          >
            <Icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </nav>
      <div className="p-3 border-t border-gray-800 text-xs text-gray-500">InfographicX v0.1</div>
    </aside>
  );
}
