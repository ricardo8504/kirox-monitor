import { type FormEvent, useState, useEffect } from "react";
import { Modal, Button, Input } from "@/components/ui";
import { useCreateServer, useUpdateServer } from "@/hooks/useServers";
import type { Server, ServerCreate, ServerUpdate, ServerType, Environment } from "@/types";

interface ServerFormModalProps {
  open: boolean;
  onClose: () => void;
  server?: Server;
}

const EMPTY_FORM: ServerCreate = {
  name: "",
  host: "",
  port: 22,
  ssh_user: "root",
  ssh_password: "",
  server_type: "PRODUCTION",
  environment: "PRODUCTION",
  monitoring_interval: 60,
  odoo_port: 8069,
  db_port: 5432,
  db_user: "postgres",
  db_password: "",
};

export function ServerFormModal({ open, onClose, server }: ServerFormModalProps) {
  const isEdit = !!server;
  const [form, setForm] = useState<ServerCreate>(EMPTY_FORM);
  const createMutation = useCreateServer();
  const updateMutation = useUpdateServer(server?.id ?? "");

  useEffect(() => {
    if (server) {
      setForm({
        name: server.name,
        host: server.host,
        port: server.port,
        ssh_user: server.ssh_user,
        ssh_password: "",
        server_type: server.server_type,
        environment: server.environment,
        monitoring_interval: server.monitoring_interval,
        odoo_port: server.odoo_port,
        db_port: server.db_port,
        db_user: server.db_user,
        db_password: "",
      });
    } else {
      setForm(EMPTY_FORM);
    }
  }, [server, open]);

  const set = (field: keyof ServerCreate, value: string | number) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (isEdit) {
      const update: ServerUpdate = {
        name: form.name,
        host: form.host,
        port: form.port,
        ssh_user: form.ssh_user,
        server_type: form.server_type,
        environment: form.environment,
        monitoring_interval: form.monitoring_interval,
        odoo_port: form.odoo_port,
        db_port: form.db_port,
        db_user: form.db_user,
      };
      if (form.ssh_password) update.ssh_password = form.ssh_password;
      if (form.db_password) update.db_password = form.db_password;
      await updateMutation.mutateAsync(update);
    } else {
      await createMutation.mutateAsync(form);
    }
    onClose();
  };

  const isPending = createMutation.isPending || updateMutation.isPending;
  const isError = createMutation.isError || updateMutation.isError;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Editar servidor" : "Agregar servidor"}
      size="lg"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Cancelar
          </Button>
          <Button size="sm" form="server-form" type="submit" loading={isPending}>
            {isEdit ? "Guardar cambios" : "Crear"}
          </Button>
        </>
      }
    >
      <form id="server-form" onSubmit={(e) => void handleSubmit(e)} className="space-y-4">

        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Conexión SSH</p>

        <Input
          id="name"
          label="Nombre"
          required
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          placeholder="Producción Odoo"
        />

        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <Input
              id="host"
              label="Host / IP"
              required
              value={form.host}
              onChange={(e) => set("host", e.target.value)}
              placeholder="10.0.0.1"
            />
          </div>
          <Input
            id="port"
            label="Puerto SSH"
            type="number"
            value={form.port ?? 22}
            onChange={(e) => set("port", Number(e.target.value))}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Input
            id="ssh_user"
            label="Usuario SSH"
            required={!isEdit}
            value={form.ssh_user}
            onChange={(e) => set("ssh_user", e.target.value)}
          />
          <Input
            id="ssh_password"
            label={isEdit ? "Contraseña SSH (dejar vacío para no cambiar)" : "Contraseña SSH"}
            type="password"
            value={form.ssh_password ?? ""}
            onChange={(e) => set("ssh_password", e.target.value)}
          />
        </div>

        <div className="border-t border-gray-700 pt-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">Servicios</p>
          <div className="grid grid-cols-3 gap-3">
            <Input
              id="odoo_port"
              label="Puerto Odoo"
              type="number"
              value={form.odoo_port ?? 8069}
              onChange={(e) => set("odoo_port", Number(e.target.value))}
            />
            <Input
              id="db_port"
              label="Puerto PostgreSQL"
              type="number"
              value={form.db_port ?? 5432}
              onChange={(e) => set("db_port", Number(e.target.value))}
            />
            <Input
              id="db_user"
              label="Usuario BD"
              value={form.db_user ?? "postgres"}
              onChange={(e) => set("db_user", e.target.value)}
            />
          </div>
          <div className="mt-3">
            <Input
              id="db_password"
              label={isEdit ? "Contraseña BD (dejar vacío para no cambiar)" : "Contraseña BD (opcional)"}
              type="password"
              value={form.db_password ?? ""}
              onChange={(e) => set("db_password", e.target.value)}
            />
          </div>
        </div>

        <div className="border-t border-gray-700 pt-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">Configuración</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label htmlFor="server_type" className="block text-xs font-medium text-gray-400">
                Tipo
              </label>
              <select
                id="server_type"
                value={form.server_type}
                onChange={(e) => set("server_type", e.target.value as ServerType)}
                className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option value="PRODUCTION">Producción</option>
                <option value="STAGING">Staging</option>
                <option value="DEVELOPMENT">Desarrollo</option>
              </select>
            </div>
            <div className="space-y-1">
              <label htmlFor="environment" className="block text-xs font-medium text-gray-400">
                Ambiente
              </label>
              <select
                id="environment"
                value={form.environment}
                onChange={(e) => set("environment", e.target.value as Environment)}
                className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option value="PRODUCTION">Producción</option>
                <option value="STAGING">Staging</option>
                <option value="DEVELOPMENT">Desarrollo</option>
              </select>
            </div>
          </div>
          <div className="mt-3">
            <Input
              id="monitoring_interval"
              label="Intervalo de monitoreo (segundos, mínimo 60)"
              type="number"
              value={form.monitoring_interval ?? 60}
              onChange={(e) => set("monitoring_interval", Math.max(60, Number(e.target.value)))}
            />
          </div>
        </div>

        {isError && (
          <p className="text-xs text-red-400">
            {isEdit
              ? "Error al actualizar el servidor."
              : "Error al crear el servidor. Verifica las credenciales e intenta de nuevo."}
          </p>
        )}
      </form>
    </Modal>
  );
}
