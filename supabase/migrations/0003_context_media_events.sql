create table public.context_records (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  device_id uuid references public.devices(id) on delete set null, stream_id uuid references public.data_streams(id) on delete set null,
  sequence_no bigint check(sequence_no >= 0), context_type public.context_type_enum not null, occurred_at timestamptz not null,
  received_at timestamptz not null default now(), payload jsonb not null, accuracy_m numeric check(accuracy_m is null or accuracy_m >= 0),
  privacy_level public.privacy_level_enum not null, checksum text check(checksum is null or checksum ~ '^sha256:[a-f0-9]{64}$'), created_at timestamptz not null default now()
);
create table public.media_assets (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  device_id uuid not null references public.devices(id) on delete restrict, stream_id uuid not null references public.data_streams(id) on delete restrict,
  sequence_no bigint not null check(sequence_no >= 0), media_type public.media_type_enum not null, occurred_at timestamptz not null, ended_at timestamptz,
  storage_bucket text not null, storage_path text not null, content_type text not null, byte_size bigint not null check(byte_size > 0),
  sha256 text not null check(sha256 ~ '^[a-f0-9]{64}$'), retention_until timestamptz not null, upload_status public.upload_status_enum not null default 'pending',
  created_at timestamptz not null default now(), deleted_at timestamptz, check(ended_at is null or ended_at >= occurred_at)
);
create table public.memory_events (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  capture_session_id uuid, started_at timestamptz not null, ended_at timestamptz not null, status public.event_status_enum not null default 'open',
  revision_no integer not null default 1 check(revision_no > 0), event_type text not null default 'context', summary text,
  importance smallint not null default 0 check(importance between 0 and 100), confidence numeric not null default 0 check(confidence between 0 and 1),
  privacy_level public.privacy_level_enum not null default 'private', created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check(ended_at >= started_at)
);
create trigger memory_events_updated_at before update on public.memory_events for each row execute function public.set_updated_at();
create table public.event_sources (
  event_id uuid not null references public.memory_events(id) on delete cascade, source_type public.source_type_enum not null, source_id uuid not null,
  relevance numeric not null check(relevance between 0 and 1), start_offset_ms integer, end_offset_ms integer, created_at timestamptz not null default now(),
  primary key(event_id, source_type, source_id), check(end_offset_ms is null or start_offset_ms is null or end_offset_ms >= start_offset_ms)
);
