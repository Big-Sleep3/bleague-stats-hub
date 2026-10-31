-- Private staff-only B.LEAGUE recruitment notes.
-- Only administrators already approved in recruiting_staff can approve new users.
create table if not exists public.bleague_contract_notes (
  player_id text primary key check (length(player_id) between 1 and 100),
  payload jsonb not null default '{}'::jsonb check (jsonb_typeof(payload)='object' and pg_column_size(payload)<40000),
  updated_by uuid not null references auth.users(id),
  updated_at timestamptz not null default now()
);
alter table public.bleague_contract_notes enable row level security;
drop policy if exists "approved staff read contracts" on public.bleague_contract_notes;
create policy "approved staff read contracts" on public.bleague_contract_notes
  for select to authenticated using ((select recruiting_private.is_approved()));
drop policy if exists "approved staff insert contracts" on public.bleague_contract_notes;
create policy "approved staff insert contracts" on public.bleague_contract_notes
  for insert to authenticated
  with check ((select recruiting_private.is_approved()) and updated_by=(select auth.uid()));
drop policy if exists "approved staff update contracts" on public.bleague_contract_notes;
create policy "approved staff update contracts" on public.bleague_contract_notes
  for update to authenticated
  using ((select recruiting_private.is_approved()))
  with check ((select recruiting_private.is_approved()) and updated_by=(select auth.uid()));
revoke all on public.bleague_contract_notes from anon,authenticated;
grant select,insert,update on public.bleague_contract_notes to authenticated;
