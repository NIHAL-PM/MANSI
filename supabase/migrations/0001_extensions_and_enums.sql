create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;
create extension if not exists vector;
create extension if not exists pg_trgm;

create type public.device_type_enum as enum ('android_phone','xiao_sense','xiaozhi_speaker','web_client','integration');
create type public.device_status_enum as enum ('active','offline','revoked');
create type public.stream_type_enum as enum ('camera','audio','location','notification','calendar','device_state','playback');
create type public.stream_state_enum as enum ('active','paused','offline','closed','revoked');
create type public.context_type_enum as enum ('location','motion','notification','calendar','app_state','device_state','playback_state','user_action');
create type public.media_type_enum as enum ('image','audio','video');
create type public.privacy_level_enum as enum ('private','sensitive','shared_caregiver');
create type public.upload_status_enum as enum ('pending','uploaded','verified','failed','expired','deleted');
create type public.event_status_enum as enum ('open','stabilized','closed','deleted');
create type public.source_type_enum as enum ('context_record','media_asset','transcript_segment','visual_observation','face_encounter','integration_record');
create type public.embedding_modality_enum as enum ('image','text','audio','face');
create type public.consent_state_enum as enum ('not_recorded','approved','revoked');
create type public.face_match_status_enum as enum ('unknown','possible_match','confirmed','rejected');
create type public.annotation_status_enum as enum ('unreviewed','user_confirmed','user_rejected','deleted');
create type public.verification_status_enum as enum ('model_inferred','user_confirmed','user_rejected');
create type public.integration_provider_enum as enum ('android_calendar','notification_listener');
create type public.integration_status_enum as enum ('active','paused','revoked','error');
create type public.policy_decision_enum as enum ('ask_now','notify_later','store_quietly','blocked');
create type public.proactive_status_enum as enum ('pending','scheduled','shown','accepted','dismissed','expired','blocked');
create type public.action_status_enum as enum ('proposed','awaiting_confirmation','confirmed','executing','succeeded','failed','cancelled');
create type public.actor_type_enum as enum ('user','device','service','worker','admin');

create or replace function public.set_updated_at()
returns trigger language plpgsql security invoker set search_path = public as $$
begin new.updated_at = now(); return new; end;
$$;
