-- Non-sensitive fixtures. This script never creates auth identities, passwords,
-- media, biometric data, location data, or device credentials. It seeds only
-- when the local test harness has already created this fixture auth user.
do $$
declare
  fixture_user_id constant uuid := '00000000-0000-0000-0000-000000000101';
  fixture_device_id constant uuid := '00000000-0000-0000-0000-000000000102';
begin
  if exists (select 1 from auth.users where id = fixture_user_id) then
    insert into public.profiles (id, timezone, capture_enabled, retention_policy, proactivity_preferences)
    values (fixture_user_id, 'UTC', false, '{"raw_media_days":1,"derived_context_days":1}'::jsonb, '{"enabled":false,"quiet_hours":[]}'::jsonb)
    on conflict (id) do nothing;

    insert into public.devices (id, user_id, device_type, display_name, public_key, firmware_version, status)
    values (fixture_device_id, fixture_user_id, 'xiao_sense', 'Fixture XIAO Sense', 'fixture-public-key-not-a-secret-000000000001', '0.0.0-test', 'offline')
    on conflict (id) do nothing;

    insert into public.data_streams (user_id, device_id, stream_type, state, sampling_config)
    values (fixture_user_id, fixture_device_id, 'camera', 'offline', '{"fps":1,"fixture":true}'::jsonb)
    on conflict do nothing;
  end if;
end;
$$;
