-- Runs automatically the first time the Postgres container starts.
-- Creates the schema and loads the CSVs mounted at /csv_data.
--
-- Note what is NOT here: no graph, no nodes, no edges. These are five
-- ordinary relational tables of the kind any airline or travel company
-- already has. The graph is created later, purely by schema.json, and
-- no data is copied to make it.

CREATE SCHEMA IF NOT EXISTS air;

-- ---------------------------------------------------------------- countries
CREATE TABLE air.countries (
    country_id    TEXT PRIMARY KEY,
    country_name  TEXT
);

-- ----------------------------------------------------------------- airports
-- Keyed on the IATA code you see on your boarding pass: SEA, KTM, CDG.
CREATE TABLE air.airports (
    iata         TEXT PRIMARY KEY,
    name         TEXT,
    city         TEXT,
    country_id   TEXT,
    latitude     DOUBLE PRECISION,
    longitude    DOUBLE PRECISION,
    altitude_ft  INTEGER,
    timezone     TEXT
);

-- ----------------------------------------------------------------- airlines
CREATE TABLE air.airlines (
    airline_id  TEXT PRIMARY KEY,
    name        TEXT,
    iata        TEXT,
    icao        TEXT,
    country_id  TEXT,
    is_active   INTEGER
);

-- ------------------------------------------------------------ flight_routes
-- One row per airport pair, however many airlines fly it. Five carriers on
-- SEA->LAX is ONE connection when you are routing a passenger.
-- distance_km was computed from coordinates with the haversine formula.
CREATE TABLE air.flight_routes (
    pair_id        TEXT PRIMARY KEY,
    src_iata       TEXT,
    dst_iata       TEXT,
    airline_count  INTEGER,
    airlines       TEXT,
    distance_km    INTEGER,
    is_domestic    INTEGER
);

-- --------------------------------------------------------- airline_airports
CREATE TABLE air.airline_airports (
    serves_id   TEXT PRIMARY KEY,
    airline_id  TEXT,
    iata        TEXT
);

-- --------------------------------------------------------------------- load
COPY air.countries        FROM '/csv_data/countries.csv'        WITH (FORMAT csv, HEADER true);
COPY air.airports         FROM '/csv_data/airports.csv'         WITH (FORMAT csv, HEADER true);
COPY air.airlines         FROM '/csv_data/airlines.csv'         WITH (FORMAT csv, HEADER true);
COPY air.flight_routes    FROM '/csv_data/flight_routes.csv'    WITH (FORMAT csv, HEADER true);
COPY air.airline_airports FROM '/csv_data/airline_airports.csv' WITH (FORMAT csv, HEADER true);

-- ------------------------------------------------------------- foreign keys
-- Declared after loading so the COPY order does not matter. These are the
-- relationships PuppyGraph will read as edges.
ALTER TABLE air.airports
    ADD CONSTRAINT fk_airports_country
    FOREIGN KEY (country_id) REFERENCES air.countries (country_id);

ALTER TABLE air.airlines
    ADD CONSTRAINT fk_airlines_country
    FOREIGN KEY (country_id) REFERENCES air.countries (country_id);

ALTER TABLE air.flight_routes
    ADD CONSTRAINT fk_routes_src FOREIGN KEY (src_iata) REFERENCES air.airports (iata),
    ADD CONSTRAINT fk_routes_dst FOREIGN KEY (dst_iata) REFERENCES air.airports (iata);

ALTER TABLE air.airline_airports
    ADD CONSTRAINT fk_serves_airline FOREIGN KEY (airline_id) REFERENCES air.airlines (airline_id),
    ADD CONSTRAINT fk_serves_airport FOREIGN KEY (iata)       REFERENCES air.airports (iata);

-- ---------------------------------------------------------------- indexes
CREATE INDEX idx_routes_src ON air.flight_routes (src_iata);
CREATE INDEX idx_routes_dst ON air.flight_routes (dst_iata);
CREATE INDEX idx_serves_iata ON air.airline_airports (iata);

-- ------------------------------------------------------------------ report
DO $$
DECLARE
    n_air INT; n_rou INT; n_ail INT;
BEGIN
    SELECT count(*) INTO n_air FROM air.airports;
    SELECT count(*) INTO n_rou FROM air.flight_routes;
    SELECT count(*) INTO n_ail FROM air.airlines;
    RAISE NOTICE 'Loaded % airports, % routes, % airlines', n_air, n_rou, n_ail;
END $$;
