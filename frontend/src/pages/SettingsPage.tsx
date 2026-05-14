import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { useNotificationChannels, useCreateChannel, useDeleteChannel } from "@/hooks/useAlerts";
import {
  Button,
  Badge,
  Card,
  Modal,
  Input,
  Spinner,
  EmptyState,
  Table,
} from "@/components/ui";
import type {
  NotificationChannel,
  ChannelType,
  EmailConfig,
  TelegramConfig,
  WebhookConfig,
} from "@/types";

const CHANNEL_LABELS: Record<ChannelType, string> = {
  EMAIL: "Email (SMTP)",
  TELEGRAM: "Telegram Bot",
  WEBHOOK: "Webhook",
};

function ChannelForm({
  type,
  onChange,
}: {
  type: ChannelType;
  onChange: (config: EmailConfig | TelegramConfig | WebhookConfig) => void;
}) {
  const [bot, setBot] = useState("");
  const [chat, setChat] = useState("");
  const [url, setUrl] = useState("");
  const [host, setHost] = useState("");
  const [smtpPort, setSmtpPort] = useState("587");
  const [smtpUser, setSmtpUser] = useState("");
  const [smtpPass, setSmtpPass] = useState("");
  const [fromEmail, setFromEmail] = useState("");
  const [toEmails, setToEmails] = useState("");

  if (type === "TELEGRAM") {
    return (
      <div className="space-y-3">
        <Input
          id="bot_token"
          label="Bot Token"
          value={bot}
          onChange={(e) => {
            setBot(e.target.value);
            onChange({ bot_token: e.target.value, chat_id: chat });
          }}
          placeholder="123456:ABC..."
        />
        <Input
          id="chat_id"
          label="Chat ID"
          value={chat}
          onChange={(e) => {
            setChat(e.target.value);
            onChange({ bot_token: bot, chat_id: e.target.value });
          }}
          placeholder="-1001234567890"
        />
      </div>
    );
  }

  if (type === "WEBHOOK") {
    return (
      <Input
        id="webhook_url"
        label="URL"
        value={url}
        onChange={(e) => {
          setUrl(e.target.value);
          onChange({ url: e.target.value });
        }}
        placeholder="https://hooks.example.com/..."
      />
    );
  }

  const emitEmail = (overrides: Partial<{
    host: string; port: string; user: string; pass: string; from: string; to: string;
  }>) => {
    const h = overrides.host ?? host;
    const p = overrides.port ?? smtpPort;
    const u = overrides.user ?? smtpUser;
    const pw = overrides.pass ?? smtpPass;
    const fr = overrides.from ?? fromEmail;
    const t = overrides.to ?? toEmails;
    onChange({
      smtp_host: h,
      smtp_port: Number(p),
      smtp_user: u,
      smtp_password: pw,
      from_email: fr,
      to_emails: t.split(",").map((s) => s.trim()).filter(Boolean),
      use_tls: true,
    });
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2">
          <Input id="smtp_host" label="SMTP Host" value={host}
            onChange={(e) => { setHost(e.target.value); emitEmail({ host: e.target.value }); }} />
        </div>
        <Input id="smtp_port" label="Port" type="number" value={smtpPort}
          onChange={(e) => { setSmtpPort(e.target.value); emitEmail({ port: e.target.value }); }} />
      </div>
      <Input id="smtp_user" label="Username" value={smtpUser}
        onChange={(e) => { setSmtpUser(e.target.value); emitEmail({ user: e.target.value }); }} />
      <Input id="smtp_password" label="Password" type="password" value={smtpPass}
        onChange={(e) => { setSmtpPass(e.target.value); emitEmail({ pass: e.target.value }); }} />
      <Input id="from_email" label="From Email" value={fromEmail}
        onChange={(e) => { setFromEmail(e.target.value); emitEmail({ from: e.target.value }); }} />
      <Input id="to_emails" label="To Emails (comma-separated)" value={toEmails}
        onChange={(e) => { setToEmails(e.target.value); emitEmail({ to: e.target.value }); }} />
    </div>
  );
}

export function SettingsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [channelType, setChannelType] = useState<ChannelType>("TELEGRAM");
  const [channelName, setChannelName] = useState("");
  const [channelConfig, setChannelConfig] = useState<
    EmailConfig | TelegramConfig | WebhookConfig | null
  >(null);

  const { data: channels, isLoading } = useNotificationChannels();
  const createMutation = useCreateChannel();
  const deleteMutation = useDeleteChannel();

  const handleClose = () => {
    setShowCreate(false);
    setChannelName("");
    setChannelConfig(null);
    setChannelType("TELEGRAM");
  };

  const columns = [
    {
      key: "name",
      header: "Channel",
      render: (c: NotificationChannel) => c.name,
    },
    {
      key: "type",
      header: "Type",
      render: (c: NotificationChannel) => (
        <span className="text-gray-400 text-xs">{CHANNEL_LABELS[c.channel_type]}</span>
      ),
    },
    {
      key: "enabled",
      header: "Enabled",
      render: (c: NotificationChannel) => (
        <Badge variant={c.enabled ? "success" : "default"}>
          {c.enabled ? "Yes" : "No"}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (c: NotificationChannel) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => deleteMutation.mutate(c.id)}
          disabled={deleteMutation.isPending}
        >
          <Trash2 className="w-4 h-4 text-red-400" />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold text-white">Settings</h1>

      <Card
        title="Notification Channels"
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4" /> Add Channel
          </Button>
        }
      >
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : (
          <Table
            columns={columns}
            rows={channels ?? []}
            keyFn={(c) => c.id}
            emptyContent={
              <EmptyState
                title="No notification channels"
                description="Add an email, Telegram or webhook channel to receive alerts."
                action={
                  <Button size="sm" onClick={() => setShowCreate(true)}>
                    <Plus className="w-4 h-4" /> Add Channel
                  </Button>
                }
              />
            }
          />
        )}
      </Card>

      <Modal
        open={showCreate}
        onClose={handleClose}
        title="Add Notification Channel"
        size="md"
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              size="sm"
              loading={createMutation.isPending}
              disabled={!channelName || !channelConfig}
              onClick={() => {
                if (!channelConfig) return;
                createMutation.mutate(
                  { channel_type: channelType, name: channelName, config: channelConfig },
                  { onSuccess: handleClose },
                );
              }}
            >
              Save
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-400">Channel Type</label>
            <div className="flex gap-2">
              {(["TELEGRAM", "EMAIL", "WEBHOOK"] as ChannelType[]).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => { setChannelType(t); setChannelConfig(null); }}
                  className={`px-3 py-1.5 text-xs rounded-md font-medium transition-colors ${
                    channelType === t
                      ? "bg-brand-600 text-white"
                      : "bg-gray-800 text-gray-400 hover:text-white"
                  }`}
                >
                  {CHANNEL_LABELS[t]}
                </button>
              ))}
            </div>
          </div>

          <Input
            id="channel_name"
            label="Channel Name"
            value={channelName}
            onChange={(e) => setChannelName(e.target.value)}
            placeholder="My Telegram"
          />

          <ChannelForm type={channelType} onChange={setChannelConfig} />

          {createMutation.isError && (
            <p className="text-xs text-red-400">Failed to create channel.</p>
          )}
        </div>
      </Modal>
    </div>
  );
}
