import { Bell, XCircle } from "lucide-react";
import { useAlertEvents, useAlertRules, useResolveEvent } from "@/hooks/useAlerts";
import { Badge, Button, Card, Table, Spinner, EmptyState } from "@/components/ui";
import type { AlertEvent, AlertRule, AlertSeverity } from "@/types";

const SEVERITY_VARIANT: Record<AlertSeverity, "info" | "warning" | "danger"> = {
  INFO: "info",
  WARNING: "warning",
  CRITICAL: "danger",
};

const CONDITION_LABEL: Record<string, string> = {
  GREATER_THAN: ">",
  LESS_THAN: "<",
  EQUALS: "=",
};

type Tab = "events" | "rules";
import { useState } from "react";

export function AlertsPage() {
  const [tab, setTab] = useState<Tab>("events");

  const { data: events = [], isLoading: eventsLoading } = useAlertEvents();
  const { data: rules = [], isLoading: rulesLoading } = useAlertRules();
  const resolveMutation = useResolveEvent();

  const eventColumns = [
    {
      key: "severity",
      header: "Severity",
      render: (e: AlertEvent) => (
        <Badge variant={SEVERITY_VARIANT[e.severity]}>{e.severity}</Badge>
      ),
    },
    {
      key: "message",
      header: "Message",
      render: (e: AlertEvent) => (
        <span className="text-gray-200">{e.message}</span>
      ),
    },
    {
      key: "value",
      header: "Value",
      render: (e: AlertEvent) => (
        <span className="font-mono text-xs">{e.metric_value.toFixed(2)}</span>
      ),
    },
    {
      key: "triggered",
      header: "Triggered",
      render: (e: AlertEvent) => new Date(e.created_at).toLocaleString(),
    },
    {
      key: "resolved",
      header: "Resolved",
      render: (e: AlertEvent) =>
        e.resolved_at ? (
          <span className="text-green-400 text-xs">
            {new Date(e.resolved_at).toLocaleString()}
          </span>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            title="Resolve"
            onClick={() => resolveMutation.mutate(e.id)}
            disabled={resolveMutation.isPending}
          >
            <XCircle className="w-4 h-4 text-green-400" />
          </Button>
        ),
    },
  ];

  const ruleColumns = [
    {
      key: "metric",
      header: "Metric",
      render: (r: AlertRule) => (
        <span className="font-mono text-xs text-gray-300">{r.metric_type}</span>
      ),
    },
    {
      key: "condition",
      header: "Condition",
      render: (r: AlertRule) => (
        <span className="font-mono text-xs">
          {CONDITION_LABEL[r.condition] ?? r.condition} {r.threshold}
        </span>
      ),
    },
    {
      key: "severity",
      header: "Severity",
      render: (r: AlertRule) => (
        <Badge variant={SEVERITY_VARIANT[r.severity]}>{r.severity}</Badge>
      ),
    },
    {
      key: "cooldown",
      header: "Cooldown",
      render: (r: AlertRule) => `${r.cooldown_minutes} min`,
    },
    {
      key: "enabled",
      header: "Enabled",
      render: (r: AlertRule) => (
        <Badge variant={r.enabled ? "success" : "default"}>
          {r.enabled ? "Yes" : "No"}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Alerts
        </h1>
        <div className="flex gap-1 p-1 bg-gray-800 rounded-lg">
          {(["events", "rules"] as Tab[]).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors capitalize ${
                tab === t
                  ? "bg-gray-700 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {tab === "events" && (
        <Card>
          {eventsLoading ? (
            <div className="flex justify-center py-8"><Spinner /></div>
          ) : (
            <Table
              columns={eventColumns}
              rows={events}
              keyFn={(e) => e.id}
              emptyContent={<EmptyState title="No alerts" description="All systems running normally." />}
            />
          )}
        </Card>
      )}

      {tab === "rules" && (
        <Card>
          {rulesLoading ? (
            <div className="flex justify-center py-8"><Spinner /></div>
          ) : (
            <Table
              columns={ruleColumns}
              rows={rules}
              keyFn={(r) => r.id}
              emptyContent={<EmptyState title="No rules" description="Create alert rules from a server's detail page." />}
            />
          )}
        </Card>
      )}
    </div>
  );
}
