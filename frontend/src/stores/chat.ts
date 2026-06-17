import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ChatState {
  messages: Message[];
  send: (content: string) => Promise<void>;
}

export const useChat = create<ChatState>((set, get) => ({
  messages: [],
  send: async (content) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content };
    set({ messages: [...get().messages, userMsg] });
    const reply: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "Received — pipeline queued.",
    };
    set({ messages: [...get().messages, reply] });
  },
}));
