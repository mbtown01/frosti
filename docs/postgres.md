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
pg_dump \
    --host ${YOUR_THERMOSTAT_HOST} \
    --username rpt rpt --clean  > /tmp/dump.dat
psql \
    --host postgres \
    --file /tmp/dump.dat rpt rpt
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
    NOW() as time,
    avg(delta*lastCooling) average
from (
    select
        lag(cooling) over (order by time) as lastCooling,
        extract(epoch from time-lag(time) over (order by time)) as delta
    from thermostat_state
    where time > NOW() - INTERVAL '1 DAY'
    ) as foo
where
    lastCooling > 0
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
