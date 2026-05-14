import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "@/api/alerts";
import type { AlertRuleCreate, AlertRuleUpdate, NotificationChannelCreate } from "@/types";

const RULES_KEY = ["alert-rules"] as const;
const EVENTS_KEY = ["alert-events"] as const;
const CHANNELS_KEY = ["alert-channels"] as const;

export function useAlertRules(params?: { server_id?: string }) {
  return useQuery({
    queryKey: [...RULES_KEY, params],
    queryFn: () => alertsApi.listRules(params),
    staleTime: 30_000,
  });
}

export function useAlertEvents(params?: { limit?: number }) {
  return useQuery({
    queryKey: [...EVENTS_KEY, params],
    queryFn: () => alertsApi.listEvents(params),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useCreateAlertRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlertRuleCreate) => alertsApi.createRule(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
  });
}

export function useUpdateAlertRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AlertRuleUpdate }) =>
      alertsApi.updateRule(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
  });
}

export function useDeleteAlertRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => alertsApi.deleteRule(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
  });
}

export function useResolveEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => alertsApi.resolveEvent(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: EVENTS_KEY }),
  });
}

export function useNotificationChannels() {
  return useQuery({
    queryKey: CHANNELS_KEY,
    queryFn: () => alertsApi.listChannels(),
    staleTime: 60_000,
  });
}

export function useCreateChannel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: NotificationChannelCreate) => alertsApi.createChannel(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHANNELS_KEY }),
  });
}

export function useDeleteChannel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => alertsApi.deleteChannel(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHANNELS_KEY }),
  });
}
