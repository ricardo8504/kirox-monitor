import { type FormEvent, useState } from "react";
import { Modal, Button, Input } from "@/components/ui";
import { useCreateServer } from "@/hooks/useServers";
import type { ServerCreate, ServerType, Environment } from "@/types";

interface ServerFormModalProps {
  open: boolean;
  onClose: () => void;
}

const DEFAULT_FORM: ServerCreate = {
  name: "",
  host: "",
  port: 22,
  ssh_user: "root",
  ssh_password: "",
  server_type: "PRODUCTION",
  environment: "PRODUCTION",
};

export function ServerFormModal({ open, onClose }: ServerFormModalProps) {
  const [form, setForm] = useState<ServerCreate>(DEFAULT_FORM);
  const createMutation = useCreateServer();

  const set = (field: keyof ServerCreate, value: string | number | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await createMutation.mutateAsync(form);
    setForm(DEFAULT_FORM);
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Add Server"
      size="md"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            size="sm"
            form="server-form"
            type="submit"
            loading={createMutation.isPending}
          >
            Save
          </Button>
        </>
      }
    >
      <form
        id="server-form"
        onSubmit={(e) => void handleSubmit(e)}
        className="space-y-3"
      >
        <Input
          id="name"
          label="Name"
          required
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          placeholder="Production Odoo"
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
            label="SSH Port"
            type="number"
            value={form.port ?? 22}
            onChange={(e) => set("port", Number(e.target.value))}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            id="ssh_user"
            label="SSH User"
            required
            value={form.ssh_user}
            onChange={(e) => set("ssh_user", e.target.value)}
          />
          <Input
            id="ssh_password"
            label="SSH Password"
            type="password"
            value={form.ssh_password ?? ""}
            onChange={(e) => set("ssh_password", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label htmlFor="server_type" className="block text-xs font-medium text-gray-400">
              Type
            </label>
            <select
              id="server_type"
              value={form.server_type}
              onChange={(e) => set("server_type", e.target.value as ServerType)}
              className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="PRODUCTION">Production</option>
              <option value="STAGING">Staging</option>
              <option value="DEVELOPMENT">Development</option>
            </select>
          </div>
          <div className="space-y-1">
            <label htmlFor="environment" className="block text-xs font-medium text-gray-400">
              Environment
            </label>
            <select
              id="environment"
              value={form.environment}
              onChange={(e) => set("environment", e.target.value as Environment)}
              className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="PRODUCTION">Production</option>
              <option value="STAGING">Staging</option>
              <option value="DEVELOPMENT">Development</option>
            </select>
          </div>
        </div>
        {createMutation.isError && (
          <p className="text-xs text-red-400">
            Failed to create server. Check credentials and try again.
          </p>
        )}
      </form>
    </Modal>
  );
}
