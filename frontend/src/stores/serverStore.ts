import { create } from "zustand";
import type { Server, MetricsSnapshot } from "@/types";

interface ServerState {
  servers: Server[];
  selectedServerId: string | null;
  liveMetrics: Record<string, MetricsSnapshot>;
  setServers: (servers: Server[]) => void;
  upsertServer: (server: Server) => void;
  removeServer: (id: string) => void;
  selectServer: (id: string | null) => void;
  updateLiveMetrics: (serverId: string, snapshot: MetricsSnapshot) => void;
}

export const useServerStore = create<ServerState>()((set) => ({
  servers: [],
  selectedServerId: null,
  liveMetrics: {},

  setServers: (servers) => set({ servers }),

  upsertServer: (server) =>
    set((state) => {
      const idx = state.servers.findIndex((s) => s.id === server.id);
      if (idx === -1) return { servers: [...state.servers, server] };
      const updated = [...state.servers];
      updated[idx] = server;
      return { servers: updated };
    }),

  removeServer: (id) =>
    set((state) => ({
      servers: state.servers.filter((s) => s.id !== id),
      selectedServerId: state.selectedServerId === id ? null : state.selectedServerId,
    })),

  selectServer: (id) => set({ selectedServerId: id }),

  updateLiveMetrics: (serverId, snapshot) =>
    set((state) => ({
      liveMetrics: { ...state.liveMetrics, [serverId]: snapshot },
    })),
}));
