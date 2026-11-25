-- JFL KORP: per-account custom theme storage.
-- Run once in Supabase SQL Editor. Existing league data and careers are untouched.
create table if not exists public.jfl_user_themes (
  user_id uuid primary key references auth.users(id) on delete cascade,
  primary_color text not null default '#1688ed'
    check (primary_color ~ '^#[0-9A-Fa-f]{6}$'),
  secondary_color text not null default '#102f55'
    check (secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
  tertiary_color text not null default '#70c4ff'
    check (tertiary_color ~ '^#[0-9A-Fa-f]{6}$'),
  updated_at timestamptz not null default now()
);

alter table public.jfl_user_themes enable row level security;

drop policy if exists jfl_user_themes_select_own on public.jfl_user_themes;
create policy jfl_user_themes_select_own
  on public.jfl_user_themes for select to authenticated
  using (user_id = auth.uid());

drop policy if exists jfl_user_themes_insert_own on public.jfl_user_themes;
create policy jfl_user_themes_insert_own
  on public.jfl_user_themes for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists jfl_user_themes_update_own on public.jfl_user_themes;
create policy jfl_user_themes_update_own
  on public.jfl_user_themes for update to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

grant select, insert, update on public.jfl_user_themes to authenticated;
