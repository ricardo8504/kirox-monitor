import { useState, useCallback } from "react";
import GridLayout, { type Layout } from "react-grid-layout";
import { useNavigate } from "react-router-dom";
import { Bell, Server, Activity, LayoutDashboard } from "lucide-react";
import { useServers } from "@/hooks/useServers";
import { useAlertEvents } from "@/hooks/useAlerts";
import { Badge, Card, Spinner } from "@/components/ui";
import type { Server as ServerType, AlertEvent, AlertSeverity } from "@/types";
import { DEFAULT_LAYOUT, type DashboardLayout, type GridItem } from "@/types/dashboard";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const SEVERITY_VARIANT: Record<AlertSeverity, "danger" | "warning" | "info"> = {
  CRITICAL: "danger",
  WARNING: "warning",
  INFO: "info",
};

function KpiCard({
  title,
  value,
  icon: Icon,
  subtitle,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  subtitle?: string;
}) {
  return (
    <Card className="h-full">
      <div className="flex items-center justify-between h-full">
        <div>
          <p className="text-xs text-gray-400">{title}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        <Icon className="w-8 h-8 text-gray-600" />
      </div>
    </Card>
  );
}

const STORAGE_KEY = "dashboard-layout";

function loadLayout(): DashboardLayout {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as DashboardLayout;
  } catch {
    // ignore
  }
  return DEFAULT_LAYOUT;
}

function saveLayout(layout: DashboardLayout) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
}

export function DashboardPage() {
  const navigate = useNavigate();
  const { data: serversData, isLoading: serversLoading } = useServers();
  const { data: events = [], isLoading: eventsLoading } = useAlertEvents({ limit: 50 });
  const [dashLayout, setDashLayout] = useState<DashboardLayout>(loadLayout);

  const servers = serversData?.items ?? [];
  const activeAlerts = events.filter((e) => !e.resolved_at);

  const activeCount = servers.filter((s) => s.is_active).length;
  const inactiveCount = servers.length - activeCount;
  const criticalAlerts = activeAlerts.filter((e) => e.severity === "CRITICAL").length;

  const onLayoutChange = useCallback(
    (newGrid: Layout[]) => {
      const updated: DashboardLayout = {
        ...dashLayout,
        grid: newGrid.map((item) => ({
          i: item.i,
          x: item.x,
          y: item.y,
          w: item.w,
          h: item.h,
        })) as GridItem[],
      };
      setDashLayout(updated);
      saveLayout(updated);
    },
    [dashLayout],
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <LayoutDashboard className="w-5 h-5 text-gray-400" />
        <h1 className="text-xl font-semibold text-white">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <KpiCard
          title="Active Servers"
          value={serversLoading ? "…" : `${activeCount} / ${servers.length}`}
          icon={Server}
          subtitle={inactiveCount > 0 ? `${inactiveCount} inactive` : "All configured"}
        />
        <KpiCard
          title="Open Alerts"
          value={eventsLoading ? "…" : activeAlerts.length}
          icon={Bell}
          subtitle={criticalAlerts > 0 ? `${criticalAlerts} critical` : undefined}
        />
        <KpiCard
          title="Monitored Servers"
          value={serversLoading ? "…" : servers.length}
          icon={Activity}
        />
      </div>

      <p className="text-xs text-gray-500">
        Drag widgets to rearrange. Layout is saved automatically.
      </p>

      <GridLayout
        className="layout"
        layout={dashLayout.grid}
        cols={12}
        rowHeight={40}
        width={1200}
        onLayoutChange={onLayoutChange}
        draggableHandle=".drag-handle"
      >
        <div key="w-server-status">
          <Card className="h-full overflow-hidden" title="Server Status">
            <div className="drag-handle absolute top-0 left-0 right-0 h-8 cursor-grab" />
            {serversLoading ? (
              <div className="flex justify-center py-6">
                <Spinner />
              </div>
            ) : servers.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-6">
                No servers configured.
              </p>
            ) : (
              <ul className="space-y-1 overflow-auto max-h-48">
                {servers.map((s: ServerType) => (
                  <li key={s.id}>
                    <button
                      type="button"
                      onClick={() => navigate(`/servers/${s.id}`)}
                      className="w-full flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-800 transition-colors"
                    >
                      <span className="text-sm text-gray-200">{s.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 font-mono">{s.host}</span>
                        <Badge variant={s.is_active ? "success" : "default"}>
                          {s.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <div key="w-alerts-list">
          <Card className="h-full overflow-hidden" title="Recent Alerts">
            <div className="drag-handle absolute top-0 left-0 right-0 h-8 cursor-grab" />
            {eventsLoading ? (
              <div className="flex justify-center py-6">
                <Spinner />
              </div>
            ) : activeAlerts.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-6">
                No open alerts — all systems nominal.
              </p>
            ) : (
              <ul className="space-y-1 overflow-auto max-h-48">
                {activeAlerts.slice(0, 10).map((e: AlertEvent) => (
                  <li
                    key={e.id}
                    className="flex items-start justify-between px-2 py-1.5 rounded bg-gray-800/50"
                  >
                    <div className="min-w-0">
                      <p className="text-sm text-gray-200 truncate">{e.message}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(e.created_at).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant={SEVERITY_VARIANT[e.severity]} className="ml-2 shrink-0">
                      {e.severity}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </GridLayout>
    </div>
  );
}
