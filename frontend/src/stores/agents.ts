import { create } from "zustand";

export type AgentStatus = "idle" | "running" | "done" | "error";

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
}

interface AgentsState {
  agents: Agent[];
  addAgent: (a: Agent) => void;
  updateAgent: (id: string, patch: Partial<Agent>) => void;
}

export const useAgents = create<AgentsState>((set, get) => ({
  agents: [
    { id: "ext", name: "Extraction", role: "Extraction Agent", status: "idle" },
    { id: "story", name: "Story", role: "Story Agent", status: "idle" },
    { id: "design", name: "Design", role: "Design Agent", status: "idle" },
    { id: "chart", name: "Chart", role: "Chart Agent", status: "idle" },
  ],
  addAgent: (a) => set({ agents: [...get().agents, a] }),
  updateAgent: (id, patch) =>
    set({ agents: get().agents.map((x) => (x.id === id ? { ...x, ...patch } : x)) }),
}));
