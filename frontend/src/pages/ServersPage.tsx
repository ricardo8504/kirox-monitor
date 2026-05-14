import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, RefreshCw, Wifi, Pencil } from "lucide-react";
import { useServers, useDeleteServer, useTestConnection } from "@/hooks/useServers";
import { Button, Badge, Table, Spinner, EmptyState, Modal, Card } from "@/components/ui";
import type { Server } from "@/types";
import { ServerFormModal } from "./servers/ServerFormModal";

export function ServersPage() {
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);
  const [editTarget, setEditTarget] = useState<Server | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Server | null>(null);

  const { data, isLoading, refetch } = useServers();
  const deleteMutation = useDeleteServer();
  const testMutation = useTestConnection();

  const columns = [
    {
      key: "name",
      header: "Name",
      render: (s: Server) => (
        <button
          type="button"
          onClick={() => navigate(`/servers/${s.id}`)}
          className="text-white font-medium hover:text-brand-400 transition-colors"
        >
          {s.name}
        </button>
      ),
    },
    {
      key: "host",
      header: "Host",
      render: (s: Server) => <span className="font-mono text-xs">{s.host}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (s: Server) => (
        <Badge variant={s.is_active ? "success" : "default"}>
          {s.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
    {
      key: "type",
      header: "Type",
      render: (s: Server) => (
        <span className="text-gray-400 text-xs">
          {s.server_type} / {s.environment}
        </span>
      ),
    },
    {
      key: "last_seen",
      header: "Last Seen",
      render: (s: Server) =>
        s.last_seen
          ? new Date(s.last_seen).toLocaleString()
          : <span className="text-gray-600">—</span>,
    },
    {
      key: "actions",
      header: "",
      render: (s: Server) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => testMutation.mutate(s.id)}
            disabled={testMutation.isPending}
            title="Test connection"
          >
            <Wifi className="w-3.5 h-3.5" />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setEditTarget(s)}
            title="Editar"
          >
            <Pencil className="w-3.5 h-3.5" />
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setDeleteTarget(s)}
          >
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Servers</h1>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => void refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4" />
            Add Server
          </Button>
        </div>
      </div>

      <Card>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : (
          <Table
            columns={columns}
            rows={data?.items ?? []}
            keyFn={(s) => s.id}
            emptyContent={
              <EmptyState
                title="No servers yet"
                description="Add your first Odoo server to start monitoring."
                action={
                  <Button size="sm" onClick={() => setShowCreate(true)}>
                    <Plus className="w-4 h-4" /> Add Server
                  </Button>
                }
              />
            }
          />
        )}
      </Card>

      <ServerFormModal open={showCreate} onClose={() => setShowCreate(false)} />
      <ServerFormModal
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        server={editTarget ?? undefined}
      />

      <Modal
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Delete Server"
        size="sm"
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              loading={deleteMutation.isPending}
              onClick={() => {
                if (!deleteTarget) return;
                deleteMutation.mutate(deleteTarget.id, {
                  onSuccess: () => setDeleteTarget(null),
                });
              }}
            >
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-300">
          Are you sure you want to delete{" "}
          <strong className="text-white">{deleteTarget?.name}</strong>? This
          action cannot be undone.
        </p>
      </Modal>
    </div>
  );
}
