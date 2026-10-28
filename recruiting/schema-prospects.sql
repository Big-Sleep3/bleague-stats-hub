-- Staff-only manually registered candidates (other leagues and long-term watchlist).
create table if not exists public.recruiting_prospects (
 id text primary key check (id ~ '^MAN-[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$'),
 name text not null check (length(trim(name)) between 1 and 140),
 university text not null check (length(trim(university)) between 1 and 160),
 league text not null default '' check (length(league)<=120),
 grade smallint check (grade between 1 and 4),
 position text check (length(position)<=40),
 height smallint check (height between 140 and 250),
 created_by uuid not null references auth.users(id),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.recruiting_prospects enable row level security;
drop policy if exists "Approved prospects read" on public.recruiting_prospects;
create policy "Approved prospects read" on public.recruiting_prospects for select to authenticated
 using ((select recruiting_private.is_approved()));
drop policy if exists "Approved prospects insert" on public.recruiting_prospects;
create policy "Approved prospects insert" on public.recruiting_prospects for insert to authenticated
 with check ((select recruiting_private.is_approved()) and created_by=(select auth.uid()));
drop policy if exists "Approved prospects update own" on public.recruiting_prospects;
create policy "Approved prospects update own" on public.recruiting_prospects for update to authenticated
 using ((select recruiting_private.is_approved()) and created_by=(select auth.uid()))
 with check ((select recruiting_private.is_approved()) and created_by=(select auth.uid()));
revoke all on public.recruiting_prospects from anon, authenticated;
grant select,insert,update on public.recruiting_prospects to authenticated;
