create unique index data_stream_sequence_uq on public.context_records(stream_id, sequence_no) where sequence_no is not null;
create unique index media_stream_sequence_uq on public.media_assets(stream_id, sequence_no);
create unique index media_storage_path_uq on public.media_assets(storage_bucket, storage_path);
create index context_user_time_idx on public.context_records(user_id, occurred_at desc);
create index media_stream_time_idx on public.media_assets(stream_id, occurred_at desc);
create index events_user_time_idx on public.memory_events(user_id, started_at desc);
create index transcript_event_time_idx on public.transcript_segments(event_id, observed_start_at);
create index observations_event_idx on public.visual_observations(event_id, frame_time);
create index face_encounters_event_idx on public.face_encounters(event_id, observed_at);
create index proactive_pending_idx on public.proactive_candidates(user_id, status, priority desc) where status in ('pending','scheduled');
create index embeddings_vector_idx on public.embeddings using hnsw (embedding vector_cosine_ops);
create index face_embeddings_vector_idx on public.face_embeddings using hnsw (embedding vector_cosine_ops);

create or replace function public.expire_media_assets(now_at timestamptz default now())
returns setof uuid language sql security definer set search_path = public as $$
  update public.media_assets set upload_status = 'expired', deleted_at = now_at
  where deleted_at is null and retention_until <= now_at and upload_status not in ('deleted','expired')
  returning id;
$$;
revoke all on function public.expire_media_assets(timestamptz) from public, anon, authenticated;
