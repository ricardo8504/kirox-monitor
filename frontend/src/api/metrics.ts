import { apiClient } from "./client";
import type { MetricResponse, MetricType, OdooMetricResponse, PgMetricResponse, MetricsSnapshot } from "@/types";

export interface MetricHistoryParams {
  metric?: MetricType;
  from?: string;
  to?: string;
}

export const metricsApi = {
  getLatest: async (serverId: string): Promise<MetricsSnapshot> => {
    const [system, odoo, pg] = await Promise.all([
      apiClient
        .get<Record<MetricType, MetricResponse | null>>(
          `/servers/${serverId}/metrics/latest`,
        )
        .then((r) => r.data),
      apiClient
        .get<OdooMetricResponse | null>(`/servers/${serverId}/metrics/odoo/latest`)
        .then((r) => r.data)
        .catch(() => null),
      apiClient
        .get<PgMetricResponse | null>(`/servers/${serverId}/metrics/pg/latest`)
        .then((r) => r.data)
        .catch(() => null),
    ]);
    return { system, odoo, pg };
  },

  getHistory: (serverId: string, params?: MetricHistoryParams) =>
    apiClient
      .get<MetricResponse[]>(`/servers/${serverId}/metrics/history`, { params })
      .then((r) => r.data),
};
