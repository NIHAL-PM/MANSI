create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  timezone text not null default 'UTC',
  capture_enabled boolean not null default false,
  retention_policy jsonb not null default '{"raw_media_days":7,"derived_context_days":365}'::jsonb,
  proactivity_preferences jsonb not null default '{"enabled":false,"quiet_hours":[]}'::jsonb,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create trigger profiles_updated_at before update on public.profiles for each row execute function public.set_updated_at();

create table public.devices (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  device_type public.device_type_enum not null, display_name text not null check (char_length(display_name) between 1 and 100),
  public_key text not null unique, firmware_version text, status public.device_status_enum not null default 'active',
  last_seen_at timestamptz, created_at timestamptz not null default now(), revoked_at timestamptz
);
create unique index devices_id_user_uq on public.devices(id, user_id);
create table public.data_streams (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  device_id uuid not null, stream_type public.stream_type_enum not null,
  state public.stream_state_enum not null default 'active', started_at timestamptz not null default now(), ended_at timestamptz,
  sampling_config jsonb not null default '{}'::jsonb, last_sequence_no bigint not null default -1 check(last_sequence_no >= -1),
  created_at timestamptz not null default now(),
  constraint data_streams_device_owner_fk foreign key (device_id, user_id) references public.devices(id, user_id) on delete restrict,
  check ((ended_at is null) or ended_at >= started_at)
);
create index devices_user_idx on public.devices(user_id);
create index streams_user_state_idx on public.data_streams(user_id, state, created_at desc);
create index streams_device_idx on public.data_streams(device_id, created_at desc);
