# Working with postgres

## Get some data for development work

The scenario is that you have a thermostat in production and want to grab some
data from it to use locally. First, get a terminal in the postgres container:

```bash
docker exec -ti rpt-postgres bash
```

From there, grab the data from the running thermostat and dump it locally:

```bash
pg_dump \
    --host ${YOUR_THERMOSTAT_HOST} \
    --username rpt -a rpt \
    --table "thermostat_state" \
    --table "thermostat_targets" \
    --table "sensor_reading" \
    --table "griddy_update"> /tmp/dump.dat
```

If you have data locally, you may need to blow it away because it could
conflict with what's coming in.  If so, purge the local tables first:

```bash
for i in thermostat_state thermostat_targets sensor_reading griddy_update; do
    psql --command "delete from ${i}" rpt rpt
done
```

We have what we need now, let's put the data into the local db instance:

```bash
psql --file /tmp/dump.dat rpt rpt
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
;
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
;
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
;
```
