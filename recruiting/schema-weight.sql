alter table public.recruiting_prospects
  add column if not exists weight smallint;
alter table public.recruiting_prospects
  drop constraint if exists recruiting_prospects_weight_range;
alter table public.recruiting_prospects
  add constraint recruiting_prospects_weight_range
    check (weight between 40 and 220);
