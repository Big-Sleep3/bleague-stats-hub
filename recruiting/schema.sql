-- Apply once in a Supabase SQL editor using a privileged project administrator.
-- The client app cannot grant privileges and the service_role key must NEVER be public.
create table if not exists public.recruiting_staff (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'scout' check (role in ('admin','coach','scout')),
  approved boolean not null default false,
  created_at timestamptz not null default now()
);
create table if not exists public.recruiting_notes (
  player_id text primary key,
  payload jsonb not null default '{}'::jsonb,
  updated_by uuid not null references auth.users(id),
  updated_at timestamptz not null default now(),
  constraint payload_object check (jsonb_typeof(payload)='object')
);
-- Keep privileged membership lookup outside the API-exposed public schema.
create schema if not exists recruiting_private;
revoke all on schema recruiting_private from public;
grant usage on schema recruiting_private to authenticated;
create or replace function recruiting_private.is_approved()
returns boolean language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.recruiting_staff
    where user_id = (select auth.uid()) and approved = true
  )
$$;
revoke all on function recruiting_private.is_approved() from public;
grant execute on function recruiting_private.is_approved() to authenticated;
alter table public.recruiting_staff enable row level security;
alter table public.recruiting_notes enable row level security;
drop policy if exists "Read own membership" on public.recruiting_staff;
create policy "Read own membership" on public.recruiting_staff
  for select to authenticated using (user_id = (select auth.uid()));
drop policy if exists "Approved read" on public.recruiting_notes;
create policy "Approved read" on public.recruiting_notes
  for select to authenticated using ((select recruiting_private.is_approved()));
drop policy if exists "Approved insert" on public.recruiting_notes;
create policy "Approved insert" on public.recruiting_notes
  for insert to authenticated
  with check ((select recruiting_private.is_approved()) and updated_by=(select auth.uid()));
drop policy if exists "Approved update" on public.recruiting_notes;
create policy "Approved update" on public.recruiting_notes
  for update to authenticated
  using ((select recruiting_private.is_approved()))
  with check ((select recruiting_private.is_approved()) and updated_by=(select auth.uid()));
revoke all on public.recruiting_staff from anon, authenticated;
revoke all on public.recruiting_notes from anon, authenticated;
grant select on public.recruiting_staff to authenticated;
grant select,insert,update on public.recruiting_notes to authenticated;
-- After a staff member signs in once, approve exact Auth user UUID via SQL editor:
-- insert into public.recruiting_staff(user_id,role,approved)
-- values ('USER_UUID_FROM_AUTH_USERS','coach',true)
-- on conflict(user_id) do update set approved=true,role=excluded.role;
