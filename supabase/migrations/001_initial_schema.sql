create extension if not exists pgcrypto;

create type chat_message_role as enum (
  'user',
  'assistant',
  'system'
);

create type task_status as enum (
  'open',
  'completed'
);

create type agent_run_status as enum (
  'success',
  'needs_follow_up',
  'failed'
);

create type reminder_delivery_status as enum (
  'sent',
  'failed',
  'skipped'
);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create table chat_messages (
  id uuid primary key default gen_random_uuid(),
  role chat_message_role not null,
  content text not null,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table agent_runs (
  id uuid primary key default gen_random_uuid(),
  chat_message_id uuid references chat_messages(id) on delete set null,
  agent_name text not null,
  llm_provider text not null,
  llm_model text not null,
  status agent_run_status not null,
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  error text,
  created_at timestamptz not null default now()
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  source_chat_message_id uuid references chat_messages(id) on delete set null,
  agent_run_id uuid references agent_runs(id) on delete set null,
  title text not null,
  notes text,
  status task_status not null default 'open',
  todo_date date not null,
  reminder_start_date date not null,
  timezone text not null default 'Asia/Kolkata',
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  constraint tasks_title_not_blank check (length(trim(title)) > 0),
  constraint tasks_completed_at_matches_status check (
    (status = 'completed' and completed_at is not null)
    or
    (status = 'open' and completed_at is null)
  )
);

create trigger tasks_set_updated_at
before update on tasks
for each row
execute function set_updated_at();

create table reminder_events (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null references tasks(id) on delete cascade,
  scheduled_for timestamptz not null,
  sent_at timestamptz,
  channel text not null default 'telegram',
  status reminder_delivery_status not null,
  message text,
  error text,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create unique index reminder_events_task_scheduled_channel_idx
on reminder_events (task_id, scheduled_for, channel);

create index chat_messages_created_at_idx
on chat_messages (created_at desc);

create index agent_runs_chat_message_id_idx
on agent_runs (chat_message_id);

create index tasks_status_todo_date_idx
on tasks (status, todo_date);

create index tasks_reminder_start_date_idx
on tasks (reminder_start_date);

create index tasks_created_at_idx
on tasks (created_at desc);

create index reminder_events_scheduled_for_idx
on reminder_events (scheduled_for);

create index reminder_events_task_id_idx
on reminder_events (task_id);

alter table chat_messages enable row level security;
alter table agent_runs enable row level security;
alter table tasks enable row level security;
alter table reminder_events enable row level security;
