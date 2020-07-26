# Working with postgres

## Get some data for development work

The scenario is that you have a thermostat in production and want to grab some
data from it to use locally. First, get a terminal in the postgres container:

```bash
docker exec -ti rpt-daemon bash
```

From there, grab the data from the running thermostat you're interested in and
place it in the local docker-compose postgres instance 'postgres':

```bash
# Extract info from a specific thermostat
pg_dump --host pi-rpt-h1.local.madllama.net \
    --username rpt rpt \
    --create --schema=public --clean  > /tmp/dump.dat
# Drop the existing schema if it exists
psql \
    --host postgres \
    --command='drop schema public cascade' rpt rpt
# Import the data AND SCHEMA
psql \
    --host postgres \
    --file /tmp/dump.dat rpt rpt
```

## Upgrading schemas

When a non-trivial change to the postgres schema happens, I've created an
'upgrade-db.py' script to facilitate things outside the normal execution 
path of the thermostat logic.  It simply moves the existing schema over to
another name and does internal SELECT INTO statements to massage the data
and populate the new schema. 

```bash
PYTHONPATH=. ./scripts/upgrade-db.py --finalize
```

## Fun queries

Process the thermostat state log and show event durations

```sql
select
    time as endingTime,
    delta,
    delta*lastCooling as coolingSeconds,
    delta*lastHeating as heatingSeconds,
    delta*lastFan as fanSeconds
from (
    select
        time,
        lag(cooling) over (order by time) as lastCooling,
        lag(heating) over (order by time) as lastHeating,
        lag(fan) over (order by time) as lastFan,
        extract(epoch from time-lag(time) over (order by time)) as delta
    from thermostat_state
    ) as foo
```

Calculate the percentage of time we spend cooling over the past 24 hours

```sql
select
    NOW() as time, sum(delta*lastCooling)/3600.0/24.0 as percentCooling
from (
    select
        lag(cooling) over (order by time) as lastCooling,
        extract(epoch from time-lag(time) over (order by time)) as delta
    from thermostat_state
    where time > NOW() - INTERVAL '1 DAY'
    ) as foo
```

Calculate the percentage of time we spend cooling over the past 24 hours

```sql
select
    min(foo.time) as time, avg(foo.delta)/60.0 as "average cycle time"
from (
    select
        time,
        lag(cooling) over (order by time) as lastCooling,
        lag(heating) over (order by time) as lastHeating,
        extract(epoch from time-lag(time) over (order by time)) as delta
    from thermostat_state
    ) as foo
where
  foo.time BETWEEN '2020-05-20T15:26:45.498Z' AND '2020-05-20T18:26:45.498Z'
  and lastCooling + lastHeating > 0
group by
  floor(extract(epoch from foo.time)/60)*60
```

Old query grouping by minute that AVERAGES when we really want LAST_VALUE

```sql
SELECT
  floor(extract(epoch from "time")/60)*60 AS "time",
  max(comfort_max) AS "comfort_max"
FROM thermostat_targets
WHERE
  "time" BETWEEN '2020-05-19T18:53:14.694Z' AND '2020-05-20T18:53:14.694Z'
GROUP BY 1
ORDER BY 1
```

New query

```sql
select
    floor(extract(epoch from bar.time)/60)*60 AS "time",
    max(bar.comfort_max) AS "comfort_max"
from (
    select
        time,
        last_value(comfort_max)
        over (
            partition by floor(extract(epoch from time)/60)*60
            order by time
            range between unbounded preceding and unbounded following
        ) comfort_max
    from
        thermostat_targets
    union
    select
        '2020-05-20T08:20:33.914Z' as time,
        last_value(comfort_max)
        over (
            order by time
            range between unbounded preceding and unbounded following
        ) comfort_max
    from
        thermostat_targets
    WHERE
        "time" < '2020-05-20T08:20:33.914Z'
) bar
WHERE
    "time" BETWEEN '2020-05-20T08:20:33.914Z' AND '2020-05-20T20:20:33.914Z'
GROUP BY 1
ORDER BY 1
```

```sql
select
    NOW() as time,
    avg(delta*lastCooling)/60.0 as "average cycle time"
from (
    select
        lag(cooling) over (order by time) as lastCooling,
        extract(epoch from time-lag(time) over (order by time)) as delta
    from thermostat_state
    ) as foo
where
    lastCooling > 0
```

```sql
select
    measurement, bucket, count(bucket)
from (
    select
        NOW() as time,
        measurement,
        round(delta*value/60)*1 as bucket
    from (
        select
            'cooling' as measurement,
            lag(cooling) over (order by time) as value,
            extract(epoch from time-lag(time) over (order by time)) as delta
        from thermostat_state
        where time > NOW() - INTERVAL '1 DAY'
        union
        select
            'heating' as measurement,
            lag(heating) over (order by time) as value,
            extract(epoch from time-lag(time) over (order by time)) as delta
        from thermostat_state
        where time > NOW() - INTERVAL '1 DAY'
        ) as foo
    where
        value > 0
) as bar
group by
    measurement, bucket
order by
    bucket
```
