import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { serversApi } from "@/api/servers";
import { useServerStore } from "@/stores/serverStore";
import type { ServerCreate, ServerUpdate } from "@/types";

const SERVERS_KEY = ["servers"] as const;

export function useServers(params?: { search?: string; status?: string; page?: number }) {
  const setServers = useServerStore((s) => s.setServers);
  return useQuery({
    queryKey: [...SERVERS_KEY, params],
    queryFn: async () => {
      const data = await serversApi.list(params);
      setServers(data.items);
      return data;
    },
    staleTime: 30_000,
  });
}

export function useServer(id: string) {
  return useQuery({
    queryKey: [...SERVERS_KEY, id],
    queryFn: () => serversApi.get(id),
    staleTime: 30_000,
  });
}

export function useCreateServer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ServerCreate) => serversApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: SERVERS_KEY }),
  });
}

export function useUpdateServer(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ServerUpdate) => serversApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: SERVERS_KEY }),
  });
}

export function useDeleteServer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => serversApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: SERVERS_KEY }),
  });
}

export function useTestConnection() {
  return useMutation({
    mutationFn: (id: string) => serversApi.testConnection(id),
  });
}
