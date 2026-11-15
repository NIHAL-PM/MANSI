create table public.integration_connections (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  provider public.integration_provider_enum not null, encrypted_secret_ref text, granted_scopes text[] not null default '{}',
  status public.integration_status_enum not null default 'active', created_at timestamptz not null default now(), updated_at timestamptz not null default now(), revoked_at timestamptz
);
create trigger integration_connections_updated_at before update on public.integration_connections for each row execute function public.set_updated_at();
create table public.integration_records (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  connection_id uuid not null references public.integration_connections(id) on delete cascade, external_id text not null, record_type text not null,
  occurred_at timestamptz not null, payload jsonb not null, sync_cursor text, created_at timestamptz not null default now(), unique(connection_id, external_id, record_type)
);
create table public.proactive_candidates (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.memory_events(id) on delete set null, trigger_type text not null, prompt_text text not null, rationale jsonb not null,
  priority smallint not null check(priority between 0 and 100), policy_decision public.policy_decision_enum not null,
  status public.proactive_status_enum not null default 'pending', scheduled_for timestamptz not null, shown_at timestamptz, user_response text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create trigger proactive_candidates_updated_at before update on public.proactive_candidates for each row execute function public.set_updated_at();
create table public.agent_actions (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.memory_events(id) on delete set null, candidate_id uuid references public.proactive_candidates(id) on delete set null,
  action_type text not null, payload jsonb not null, requires_confirmation boolean not null default true, status public.action_status_enum not null default 'proposed',
  external_reference text, requested_at timestamptz not null default now(), confirmed_at timestamptz, executed_at timestamptz, result jsonb
);
create table public.audit_log (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  actor_type public.actor_type_enum not null, actor_id text not null, action text not null, resource_type text not null, resource_id uuid,
  trace_id text not null, metadata jsonb not null default '{}'::jsonb, occurred_at timestamptz not null default now(), created_at timestamptz not null default now()
);
