alter table public.profiles enable row level security;
alter table public.devices enable row level security;
alter table public.data_streams enable row level security;
alter table public.context_records enable row level security;
alter table public.media_assets enable row level security;
alter table public.memory_events enable row level security;
alter table public.event_sources enable row level security;
alter table public.transcript_segments enable row level security;
alter table public.visual_observations enable row level security;
alter table public.embeddings enable row level security;
alter table public.people enable row level security;
alter table public.face_encounters enable row level security;
alter table public.face_embeddings enable row level security;
alter table public.facts enable row level security;
alter table public.integration_connections enable row level security;
alter table public.integration_records enable row level security;
alter table public.proactive_candidates enable row level security;
alter table public.agent_actions enable row level security;
alter table public.audit_log enable row level security;

create policy profiles_owner on public.profiles for all using (id = auth.uid()) with check (id = auth.uid());
create policy devices_owner on public.devices for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy streams_owner on public.data_streams for select using (user_id = auth.uid());
create policy context_owner on public.context_records for select using (user_id = auth.uid());
create policy media_owner on public.media_assets for select using (user_id = auth.uid());
create policy events_owner on public.memory_events for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy event_sources_owner on public.event_sources for select using (exists (select 1 from public.memory_events e where e.id = event_id and e.user_id = auth.uid()));
create policy transcript_owner on public.transcript_segments for select using (user_id = auth.uid());
create policy visual_owner on public.visual_observations for select using (user_id = auth.uid());
create policy embeddings_owner on public.embeddings for select using (user_id = auth.uid());
create policy people_owner on public.people for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy encounter_owner on public.face_encounters for select using (user_id = auth.uid());
create policy face_embedding_owner on public.face_embeddings for select using (user_id = auth.uid());
create policy facts_owner on public.facts for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy connection_owner on public.integration_connections for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy record_owner on public.integration_records for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy candidate_owner on public.proactive_candidates for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy action_owner on public.agent_actions for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy audit_owner on public.audit_log for select using (user_id = auth.uid());

-- Raw media stays private; only the API service role issues signed URLs after authorization.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('private-media', 'private-media', false, 52428800, array['image/jpeg','audio/opus','audio/wav','video/mp4'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;
