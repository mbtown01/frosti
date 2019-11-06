
-- Database Thoughts
--     * Need to capture time series data for
--         * temp/pressure/humidity
--         * price
--     * Configuration data
--         * settings
--         * programs
--         * schedule
--     * Telemetry data
--         * relay flips
--         * settings changes
--         * starts/stops
--         * load/memory/etc from pi

-- Unique set of measurements that are captured
DROP TABLE IF EXISTS sample_type;
CREATE TABLE sample_type (
    id integer PRIMARY KEY,
    name text,
    description
);

INSERT INTO sample_type (id, name) values (1, 'Temperature', 'Temperature in degF');
INSERT INTO sample_type (id, name) values (2, 'Pressure', 'Pressure in Pa');
INSERT INTO sample_type (id, name) values (3, 'Humidity', 'Humidity as fraction 0-1');
INSERT INTO sample_type (id, name) values (4, 'PowerPrice', 'Price of power from provider');

DROP TABLE IF EXISTS thermostat;
CREATE TABLE thermostat (
    name text,
    useDegF boolean,
    delta real
)

INSERT INTO thermostat (id, useDegF, delta) VALUES ('testing', TRUE, 1.0)

-- time series of sample measurements
DROP TABLE IF EXISTS sample;
CREATE TABLE sample (
    sample_type_id integer REFERENCES sample_type,
    time timestamp,
    value real
);

DROP TABLE IF EXISTS targets;
CREATE TABLE targets (
    time timestamp,
    comfortMin real,
    comfortMax real
);

DROP TABLE IF EXISTS program;
CREATE TABLE program (
    name text,
    comfortMin real,
    comfortMax real,
    PRIMARY KEY(thermostat_id, name)
);

DROP TABLE IF EXISTS program_overrides;
CREATE TABLE program_overrides (
    program_name text REFERENCES program,
    price real,
    comfortMin real,
    comfortMax real
);

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule (
    name text PRIMARY KEY,
    days boolean[7]
);

DROP TABLE IF EXISTS schedule_times;
CREATE TABLE schedule_times (
    hour integer,
    minute, integer,
    program_name text REFERENCES program,
    UNIQUE(hour, minute)
);
