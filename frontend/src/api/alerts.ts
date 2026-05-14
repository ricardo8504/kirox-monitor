import { apiClient } from "./client";
import type {
  AlertRule,
  AlertRuleCreate,
  AlertRuleUpdate,
  AlertEvent,
  NotificationChannel,
  NotificationChannelCreate,
} from "@/types";

export const alertsApi = {
  // Rules
  listRules: (params?: { server_id?: string }) =>
    apiClient
      .get<AlertRule[]>("/alerts/rules", { params })
      .then((r) => r.data),

  createRule: (data: AlertRuleCreate) =>
    apiClient.post<AlertRule>("/alerts/rules", data).then((r) => r.data),

  updateRule: (id: string, data: AlertRuleUpdate) =>
    apiClient.put<AlertRule>(`/alerts/rules/${id}`, data).then((r) => r.data),

  deleteRule: (id: string) =>
    apiClient.delete(`/alerts/rules/${id}`).then((r) => r.data),

  // Events
  listEvents: (params?: { limit?: number }) =>
    apiClient
      .get<AlertEvent[]>("/alerts/events", { params })
      .then((r) => r.data),

  resolveEvent: (id: string) =>
    apiClient.post<AlertEvent>(`/alerts/events/${id}/resolve`).then((r) => r.data),

  // Notification channels
  listChannels: () =>
    apiClient.get<NotificationChannel[]>("/notifications/channels").then((r) => r.data),

  createChannel: (data: NotificationChannelCreate) =>
    apiClient
      .post<NotificationChannel>("/notifications/channels", data)
      .then((r) => r.data),

  deleteChannel: (id: string) =>
    apiClient.delete(`/notifications/channels/${id}`).then((r) => r.data),
};
