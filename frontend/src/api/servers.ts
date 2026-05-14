import { apiClient } from "./client";
import type { Server, ServerCreate, ServerUpdate, PaginatedResponse, PaginationParams } from "@/types";

export const serversApi = {
  list: (params?: PaginationParams & { search?: string }) =>
    apiClient
      .get<PaginatedResponse<Server>>("/servers", { params })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Server>(`/servers/${id}`).then((r) => r.data),

  create: (data: ServerCreate) =>
    apiClient.post<Server>("/servers", data).then((r) => r.data),

  update: (id: string, data: ServerUpdate) =>
    apiClient.put<Server>(`/servers/${id}`, data).then((r) => r.data),

  delete: (id: string) =>
    apiClient.delete(`/servers/${id}`).then((r) => r.data),

  testConnection: (id: string) =>
    apiClient
      .post<{ server_id: string; connected: boolean }>(
        `/servers/${id}/test-connection`,
      )
      .then((r) => r.data),
};
