import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Wifi, Pencil } from "lucide-react";
import { useServer, useTestConnection } from "@/hooks/useServers";
import { useLatestMetrics, useLiveMetrics, useMetricHistory } from "@/hooks/useServerMetrics";
import { Button, Badge, Card, Spinner } from "@/components/ui";
import { MetricGauge } from "@/components/metrics/MetricGauge";
import { MetricChart } from "@/components/metrics/MetricChart";
import { ServerFormModal } from "./ServerFormModal";
import type { MetricType } from "@/types";

const RANGES = [
  { label: "1h", hours: 1 },
  { label: "6h", hours: 6 },
  { label: "24h", hours: 24 },
  { label: "7d", hours: 168 },
  { label: "30d", hours: 720 },
];

interface ChartSectionProps {
  serverId: string;
  rangeHours: number;
}

function ChartSection({ serverId, rangeHours }: ChartSectionProps) {
  const charts: { metric: MetricType; label: string; color: string; unit: string }[] = [
    { metric: "CPU_USAGE", label: "CPU", color: "#f59e0b", unit: "%" },
    { metric: "RAM_USAGE", label: "RAM", color: "#3b82f6", unit: "%" },
    { metric: "DISK_USAGE", label: "Disco", color: "#10b981", unit: "%" },
    { metric: "LOAD_AVG_1", label: "Load 1m", color: "#8b5cf6", unit: "" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {charts.map(({ metric, label, color, unit }) => (
        <ChartCard
          key={metric}
          serverId={serverId}
          metric={metric}
          label={label}
          color={color}
          unit={unit}
          rangeHours={rangeHours}
        />
      ))}
    </div>
  );
}

interface ChartCardProps {
  serverId: string;
  metric: MetricType;
  label: string;
  color: string;
  unit: string;
  rangeHours: number;
}

function ChartCard({ serverId, metric, label, color, unit, rangeHours }: ChartCardProps) {
  const { data = [], isLoading } = useMetricHistory(serverId, metric, rangeHours);

  return (
    <Card title={label}>
      {isLoading ? (
        <div className="flex justify-center items-center h-40">
          <Spinner />
        </div>
      ) : data.length === 0 ? (
        <div className="flex justify-center items-center h-40 text-gray-500 text-sm">
          Sin datos para este período
        </div>
      ) : (
        <MetricChart metrics={data} label={label} color={color} unit={unit} height={160} />
      )}
    </Card>
  );
}

export function ServerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [rangeHours, setRangeHours] = useState(24);
  const [showEdit, setShowEdit] = useState(false);

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
    return <div className="text-center py-16 text-gray-400">Servidor no encontrado.</div>;
  }

  const system = liveMetrics?.system ?? latestMetrics?.system ?? {};

  const cpuVal = system.CPU_USAGE?.value ?? 0;
  const ramVal = system.RAM_USAGE?.value ?? 0;
  const diskVal = system.DISK_USAGE?.value ?? 0;
  const load1 = system.LOAD_AVG_1?.value ?? 0;
  const load5 = system.LOAD_AVG_5?.value ?? 0;
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
          {server.is_active ? "Activo" : "Inactivo"}
        </Badge>
        <div className="ml-auto flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowEdit(true)}
          >
            <Pencil className="w-4 h-4" />
            Editar
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => testMutation.mutate(server.id)}
            loading={testMutation.isPending}
          >
            <Wifi className="w-4 h-4" />
            Test SSH
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
        <Card title="Disco">
          <MetricGauge value={diskVal} label="Disco" />
        </Card>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Load 1m", value: load1.toFixed(2) },
          { label: "Load 5m", value: load5.toFixed(2) },
          { label: "Procesos", value: String(Math.round(processCount)) },
          { label: "Intervalo", value: `${server.monitoring_interval}s` },
        ].map(({ label, value }) => (
          <Card key={label}>
            <p className="text-xs text-gray-400">{label}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
          </Card>
        ))}
      </div>

      {odoo && (
        <Card title="Odoo">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-400">Workers activos</p>
              <p className="text-2xl font-bold text-white">{odoo.workers_active}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Procesos colgados</p>
              <p className="text-2xl font-bold text-yellow-400">{odoo.processes_hung}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Req. concurrentes</p>
              <p className="text-2xl font-bold text-blue-400">{odoo.requests_concurrent}</p>
            </div>
          </div>
          {odoo.response_time_ms != null && (
            <p className="text-center text-xs text-gray-400 mt-2">
              Tiempo de respuesta HTTP: <span className="text-white font-mono">{odoo.response_time_ms}ms</span>
            </p>
          )}
        </Card>
      )}

      {pg && (
        <Card title="PostgreSQL">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-400">Conexiones</p>
              <p className="text-2xl font-bold text-white">{pg.connections_active}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Locks</p>
              <p className="text-2xl font-bold text-yellow-400">{pg.locks}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Consultas lentas</p>
              <p className="text-2xl font-bold text-red-400">{pg.slow_queries}</p>
            </div>
          </div>
          <p className="text-center text-xs text-gray-400 mt-2">
            Tamaño BD: <span className="text-white font-mono">{pg.db_size_mb.toFixed(1)} MB</span>
          </p>
        </Card>
      )}

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-white">Histórico de métricas</h2>
          <div className="flex gap-1">
            {RANGES.map(({ label, hours }) => (
              <button
                key={hours}
                type="button"
                onClick={() => setRangeHours(hours)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  rangeHours === hours
                    ? "bg-brand-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <ChartSection serverId={id!} rangeHours={rangeHours} />
      </div>

      <Card title="Información del servidor">
        <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
          {[
            ["Host", server.host],
            ["Puerto SSH", String(server.port)],
            ["Usuario SSH", server.ssh_user],
            ["Puerto Odoo", String(server.odoo_port)],
            ["Puerto BD", String(server.db_port)],
            ["Usuario BD", server.db_user],
            ["Tipo", server.server_type],
            ["Ambiente", server.environment],
            ["Última conexión", server.last_seen ? new Date(server.last_seen).toLocaleString() : "—"],
          ].map(([k, v]) => (
            <div key={k} className="flex gap-2">
              <dt className="text-gray-400 shrink-0">{k}:</dt>
              <dd className="text-gray-200 font-mono truncate">{v}</dd>
            </div>
          ))}
        </dl>
      </Card>

      <ServerFormModal
        open={showEdit}
        onClose={() => setShowEdit(false)}
        server={server}
      />
    </div>
  );
}
