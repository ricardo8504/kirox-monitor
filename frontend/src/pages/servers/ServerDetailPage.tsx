import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Wifi } from "lucide-react";
import { useServer, useTestConnection } from "@/hooks/useServers";
import { useLatestMetrics, useLiveMetrics } from "@/hooks/useServerMetrics";
import { Button, Badge, Card, Spinner } from "@/components/ui";
import { MetricGauge } from "@/components/metrics/MetricGauge";

export function ServerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: server, isLoading: serverLoading } = useServer(id!);
  const { data: latestMetrics } = useLatestMetrics(id!);
  const liveMetrics = useLiveMetrics(id!);
  const testMutation = useTestConnection();

  if (serverLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!server) {
    return (
      <div className="text-center py-16 text-gray-400">Server not found.</div>
    );
  }

  const system = liveMetrics?.system ?? latestMetrics?.system ?? {};

  const cpuVal = system.CPU_USAGE?.value ?? 0;
  const ramVal = system.RAM_USAGE?.value ?? 0;
  const diskVal = system.DISK_USAGE?.value ?? 0;
  const load1 = system.LOAD_AVG_1?.value ?? 0;
  const load5 = system.LOAD_AVG_5?.value ?? 0;
  const ramMb = system.RAM_USAGE?.value ?? 0;
  const processCount = system.PROCESS_COUNT?.value ?? 0;

  const odoo = liveMetrics?.odoo ?? latestMetrics?.odoo ?? null;
  const pg = liveMetrics?.pg ?? latestMetrics?.pg ?? null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate("/servers")}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <h1 className="text-xl font-semibold text-white">{server.name}</h1>
        <Badge variant={server.is_active ? "success" : "default"}>
          {server.is_active ? "Active" : "Inactive"}
        </Badge>
        <div className="ml-auto flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => testMutation.mutate(server.id)}
            loading={testMutation.isPending}
          >
            <Wifi className="w-4 h-4" />
            Test Connection
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="CPU">
          <MetricGauge value={cpuVal} label="CPU" />
        </Card>
        <Card title="RAM">
          <MetricGauge value={ramVal} label="RAM" />
        </Card>
        <Card title="Disk">
          <MetricGauge value={diskVal} label="Disk" />
        </Card>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Load 1m", value: load1.toFixed(2) },
          { label: "Load 5m", value: load5.toFixed(2) },
          { label: "RAM Used", value: `${Math.round(ramMb / 1024)} GB` },
          { label: "Processes", value: String(Math.round(processCount)) },
        ].map(({ label, value }) => (
          <Card key={label}>
            <p className="text-xs text-gray-400">{label}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
          </Card>
        ))}
      </div>

      {odoo && (
        <Card title="Odoo Workers">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-400">Active Workers</p>
              <p className="text-2xl font-bold text-white">{odoo.workers_active}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Hung Processes</p>
              <p className="text-2xl font-bold text-yellow-400">{odoo.processes_hung}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Concurrent Req</p>
              <p className="text-2xl font-bold text-blue-400">{odoo.requests_concurrent}</p>
            </div>
          </div>
        </Card>
      )}

      {pg && (
        <Card title="PostgreSQL">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-400">Connections</p>
              <p className="text-2xl font-bold text-white">{pg.connections_active}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Locks</p>
              <p className="text-2xl font-bold text-yellow-400">{pg.locks}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Slow Queries</p>
              <p className="text-2xl font-bold text-red-400">{pg.slow_queries}</p>
            </div>
          </div>
        </Card>
      )}

      <Card title="Server Info">
        <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
          {[
            ["Host", server.host],
            ["SSH Port", String(server.port)],
            ["SSH User", server.ssh_user],
            ["Type", server.server_type],
            ["Environment", server.environment],
            ["Interval", `${server.monitoring_interval}s`],
            [
              "Last Seen",
              server.last_seen
                ? new Date(server.last_seen).toLocaleString()
                : "—",
            ],
          ].map(([k, v]) => (
            <div key={k} className="flex gap-2">
              <dt className="text-gray-400 shrink-0">{k}:</dt>
              <dd className="text-gray-200 font-mono truncate">{v}</dd>
            </div>
          ))}
        </dl>
      </Card>
    </div>
  );
}
