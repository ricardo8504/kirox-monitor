// ─── Auth ────────────────────────────────────────────────────────────────────

export type UserRole = "ADMIN" | "OPERATOR" | "READONLY";

export interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// ─── Servers ─────────────────────────────────────────────────────────────────

export type ServerType = "PRODUCTION" | "STAGING" | "DEVELOPMENT";
export type Environment = "PRODUCTION" | "STAGING" | "DEVELOPMENT";

export interface Server {
  id: string;
  name: string;
  host: string;
  port: number;
  ssh_user: string;
  server_type: ServerType;
  environment: Environment;
  monitoring_interval: number;
  odoo_port: number;
  db_port: number;
  db_user: string;
  is_active: boolean;
  last_seen: string | null;
  created_by: string | null;
  created_at: string;
}

export interface ServerCreate {
  name: string;
  host: string;
  port?: number;
  ssh_user: string;
  ssh_password?: string;
  ssh_key?: string;
  server_type: ServerType;
  environment: Environment;
  monitoring_interval?: number;
  odoo_port?: number;
  db_port?: number;
  db_user?: string;
  db_password?: string;
}

export interface ServerUpdate {
  name?: string;
  host?: string;
  port?: number;
  ssh_user?: string;
  ssh_password?: string;
  ssh_key?: string;
  server_type?: ServerType;
  environment?: Environment;
  monitoring_interval?: number;
  odoo_port?: number;
  db_port?: number;
  db_user?: string;
  db_password?: string;
  is_active?: boolean;
}

// ─── Metrics ─────────────────────────────────────────────────────────────────

export type MetricType =
  | "CPU_USAGE"
  | "RAM_USAGE"
  | "SWAP_USAGE"
  | "DISK_USAGE"
  | "DISK_IO_READ"
  | "DISK_IO_WRITE"
  | "LOAD_AVG_1"
  | "LOAD_AVG_5"
  | "LOAD_AVG_15"
  | "NETWORK_IN"
  | "NETWORK_OUT"
  | "PROCESS_COUNT"
  | "CPU_TEMP";

export interface MetricResponse {
  id: string;
  server_id: string;
  metric_type: MetricType;
  value: number;
  unit: string;
  timestamp: string;
  raw_data: Record<string, unknown> | null;
}

export interface OdooMetricResponse {
  id: string;
  server_id: string;
  workers_active: number;
  processes_hung: number;
  memory_mb: number;
  cpu_percent: number;
  response_time_ms: number | null;
  requests_concurrent: number;
  timestamp: string;
}

export interface PgMetricResponse {
  id: string;
  server_id: string;
  connections_active: number;
  slow_queries: number;
  locks: number;
  deadlocks: number;
  db_size_mb: number;
  timestamp: string;
}

export interface MetricsSnapshot {
  system: Partial<Record<MetricType, MetricResponse | null>>;
  odoo: OdooMetricResponse | null;
  pg: PgMetricResponse | null;
}

// ─── Alerts ──────────────────────────────────────────────────────────────────

export type AlertSeverity = "INFO" | "WARNING" | "CRITICAL";
export type AlertCondition = "GREATER_THAN" | "LESS_THAN" | "EQUALS";
export type ChannelType = "EMAIL" | "TELEGRAM" | "WEBHOOK";

export interface AlertRule {
  id: string;
  server_id: string;
  metric_type: MetricType;
  condition: AlertCondition;
  threshold: number;
  severity: AlertSeverity;
  enabled: boolean;
  cooldown_minutes: number;
  created_at: string;
}

export interface AlertRuleCreate {
  server_id: string;
  metric_type: MetricType;
  condition: AlertCondition;
  threshold: number;
  severity?: AlertSeverity;
  cooldown_minutes?: number;
}

export interface AlertRuleUpdate {
  threshold?: number;
  severity?: AlertSeverity;
  enabled?: boolean;
  cooldown_minutes?: number;
}

export interface AlertEvent {
  id: string;
  rule_id: string;
  server_id: string;
  severity: AlertSeverity;
  message: string;
  metric_value: number;
  notified_at: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface NotificationChannel {
  id: string;
  user_id: string;
  channel_type: ChannelType;
  name: string;
  enabled: boolean;
  created_at: string;
}

export interface NotificationChannelCreate {
  channel_type: ChannelType;
  name: string;
  config: EmailConfig | TelegramConfig | WebhookConfig;
}

export interface EmailConfig {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  from_email: string;
  to_emails: string[];
  use_tls: boolean;
}

export interface TelegramConfig {
  bot_token: string;
  chat_id: string;
}

export interface WebhookConfig {
  url: string;
  headers?: Record<string, string>;
}

// ─── WebSocket messages ───────────────────────────────────────────────────────

export interface WsMetricsMessage {
  type: "metrics";
  server_id: string;
  data: MetricsSnapshot;
}

export interface WsAlertMessage {
  type: "alert";
  data: AlertEvent;
}

export type WsMessage = WsMetricsMessage | WsAlertMessage;

// ─── Pagination ───────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// ─── API Error ────────────────────────────────────────────────────────────────

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}
