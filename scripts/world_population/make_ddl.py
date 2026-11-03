"""Prints the migration SQL for world_population_by_age (one row per location x year, one column per single year of age)
and the world_population_age_groups view. Usage: python scripts/world_population/make_ddl.py"""
cols = ',\n  '.join(f'age_{a} bigint not null' for a in range(101))
ddl = f"""create table if not exists public.world_population_by_age (
  loc_id integer not null,
  iso3 text,
  location text not null,
  loc_type text not null check (loc_type in ('world','region','subregion','country')),
  region_id integer,
  subregion_id integer,
  year integer not null,
  is_projection boolean not null,
  variant text not null default 'Medium',
  total bigint not null,
  {cols},
  source text not null default 'UN World Population Prospects 2024',
  created_at timestamptz not null default now(),
  primary key (loc_id, year, variant)
);
comment on table public.world_population_by_age is 'UN WPP 2024 medium variant, population (persons, 1 July) by single year of age, both sexes, 1950-2100 (2024+ are projections). age_100 = 100 and over. loc_type: world / 6 continental regions / 21 subregions / 237 countries and areas.';
create index if not exists world_population_by_age_year_idx on public.world_population_by_age (year);
create index if not exists world_population_by_age_type_idx on public.world_population_by_age (loc_type, year);

create or replace view public.world_population_age_groups as
select loc_id, iso3, location, loc_type, region_id, subregion_id, year, is_projection, variant, total,
  ({' + '.join(f'age_{a}' for a in range(0, 16))}) as under_16,
  ({' + '.join(f'age_{a}' for a in range(16, 65))}) as age_16_64,
  ({' + '.join(f'age_{a}' for a in range(65, 101))}) as age_65_plus,
  ({' + '.join(f'age_{a}' for a in range(0, 15))}) as age_0_14,
  ({' + '.join(f'age_{a}' for a in range(15, 65))}) as age_15_64,
  ({' + '.join(f'age_{a}' for a in range(18, 101))}) as age_18_plus,
  ({' + '.join(f'age_{a}' for a in range(80, 101))}) as age_80_plus
from public.world_population_by_age;
comment on view public.world_population_age_groups is 'Under 16 (ages 0-15), 16-64 and 65+ are mutually exclusive and add up to total; the other columns are the UN-standard 0-14 / 15-64 groups and 18+ / 80+.';
"""
print(ddl)
