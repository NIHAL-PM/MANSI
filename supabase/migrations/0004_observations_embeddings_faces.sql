create table public.transcript_segments (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.memory_events(id) on delete set null, media_asset_id uuid not null references public.media_assets(id) on delete cascade,
  observed_start_at timestamptz not null, observed_end_at timestamptz not null, processed_at timestamptz not null default now(),
  speaker_label text, text text not null, language_code text not null, confidence numeric not null check(confidence between 0 and 1),
  model_name text not null, model_version text not null, created_at timestamptz not null default now(), check(observed_end_at >= observed_start_at)
);
create table public.visual_observations (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.memory_events(id) on delete set null, media_asset_id uuid not null references public.media_assets(id) on delete cascade,
  frame_time timestamptz not null, observation_type text not null, payload jsonb not null, confidence numeric not null check(confidence between 0 and 1),
  model_name text not null, model_version text not null, processed_at timestamptz not null default now(), created_at timestamptz not null default now()
);
create table public.embeddings (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.memory_events(id) on delete set null, source_type public.source_type_enum not null, source_id uuid not null,
  modality public.embedding_modality_enum not null, model_name text not null, model_version text not null, embedding vector(768) not null, created_at timestamptz not null default now(),
  unique(source_type, source_id, modality, model_name, model_version)
);
create table public.people (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  display_name text not null, consent_state public.consent_state_enum not null default 'not_recorded', notes text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(), deleted_at timestamptz
);
create trigger people_updated_at before update on public.people for each row execute function public.set_updated_at();
create table public.face_encounters (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid not null references public.memory_events(id) on delete cascade, media_asset_id uuid not null references public.media_assets(id) on delete cascade,
  tracker_id text not null, observed_at timestamptz not null, quality_score numeric not null check(quality_score between 0 and 1),
  match_status public.face_match_status_enum not null default 'unknown', person_id uuid references public.people(id) on delete set null,
  best_similarity numeric check(best_similarity is null or best_similarity between -1 and 1), confidence numeric not null check(confidence between 0 and 1),
  annotation_status public.annotation_status_enum not null default 'unreviewed', created_at timestamptz not null default now()
);
create table public.face_embeddings (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  person_id uuid references public.people(id) on delete set null, face_encounter_id uuid not null references public.face_encounters(id) on delete cascade,
  model_name text not null, model_version text not null, embedding vector(512) not null, quality_score numeric not null check(quality_score between 0 and 1),
  verification_status public.verification_status_enum not null default 'model_inferred', created_at timestamptz not null default now()
);
create table public.facts (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid not null references public.memory_events(id) on delete cascade, fact_type text not null, fact_value jsonb not null,
  confidence numeric not null check(confidence between 0 and 1), verification_status public.verification_status_enum not null default 'model_inferred',
  created_at timestamptz not null default now(), superseded_at timestamptz
);
