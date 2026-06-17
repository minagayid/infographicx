import { create } from "zustand";

export type AppMode = "code" | "paper" | "dashboard" | "whiteboard" | "mindmap" | "flow";

interface WorkspaceState {
  mode: AppMode;
  setMode: (m: AppMode) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useWorkspace = create<WorkspaceState>((set) => ({
  mode: "flow",
  setMode: (mode) => set({ mode }),
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
