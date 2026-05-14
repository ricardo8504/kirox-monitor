export type WidgetType =
  | "server-status"
  | "cpu-gauge"
  | "ram-gauge"
  | "disk-gauge"
  | "cpu-chart"
  | "ram-chart"
  | "alerts-list"
  | "odoo-workers"
  | "pg-connections";

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  serverId?: string;
  metricRange?: "1h" | "6h" | "24h";
}

export interface GridItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DashboardLayout {
  widgets: WidgetConfig[];
  grid: GridItem[];
}

export const DEFAULT_LAYOUT: DashboardLayout = {
  widgets: [
    { id: "w-server-status", type: "server-status", title: "Server Status" },
    { id: "w-alerts-list", type: "alerts-list", title: "Open Alerts" },
  ],
  grid: [
    { i: "w-server-status", x: 0, y: 0, w: 6, h: 6 },
    { i: "w-alerts-list", x: 6, y: 0, w: 6, h: 6 },
  ],
};
