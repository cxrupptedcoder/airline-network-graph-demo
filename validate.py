#!/usr/bin/env python3
"""
Pre-flight check. Run this BEFORE `docker compose up -d`.

    pip install duckdb
    python3 validate.py

Verifies three things that are painful to debug once containers are running:

  1. init/01_load_data.sql column order matches the CSV headers exactly.
     Postgres COPY is positional — if the SQL lists columns in a different
     order than the CSV, it loads silently wrong or fails halfway.

  2. Referential integrity inside the CSVs. Every route endpoint resolves to
     a real airport, every airline to a real country, and so on. If these
     fail, the FK constraints in the SQL will abort the container's first
     boot with an error that scrolls past in the logs.

  3. schema.json only references tables and columns that actually exist,
     key arities match, and edge IDs are unique.

Exits non-zero if anything is wrong.
"""
import csv, json, os, re, sys
import duckdb

SQL = "init/01_load_data.sql"
CSV_DIR = "csv_data"
SCHEMA = "schema.json"

errors, warnings = [], []


# ------------------------------------------------ 1. SQL vs CSV column order
def sql_columns():
    """Pull the column list out of each CREATE TABLE air.<name> ( ... )."""
    text = open(SQL).read()
    out = {}
    for m in re.finditer(r"CREATE TABLE air\.(\w+)\s*\((.*?)\n\);",
                         text, re.S | re.I):
        table, body = m.group(1), m.group(2)
        cols = []
        for line in body.splitlines():
            line = line.split("--")[0].strip().rstrip(",")
            if not line or line.upper().startswith(("PRIMARY", "CONSTRAINT",
                                                    "FOREIGN", "UNIQUE")):
                continue
            cols.append(line.split()[0])
        out[table] = cols
    return out


print("=" * 64)
print("1. SQL column order vs CSV headers")
print("=" * 64)
sqlcols = sql_columns()
if not sqlcols:
    errors.append("could not parse any CREATE TABLE from " + SQL)

for table, cols in sorted(sqlcols.items()):
    path = f"{CSV_DIR}/{table}.csv"
    if not os.path.exists(path):
        errors.append(f"{table}: {path} missing")
        print(f"  FAIL {table:<20} no CSV")
        continue
    with open(path, newline="") as f:
        header = next(csv.reader(f))
    if header == cols:
        print(f"  OK   {table:<20}{len(cols)} columns match")
    else:
        errors.append(f"{table}: SQL {cols} != CSV {header}")
        print(f"  FAIL {table:<20}SQL={cols}")
        print(f"       {'':<20}CSV={header}")

# --------------------------------------------- 2. integrity inside the CSVs
print()
print("=" * 64)
print("2. Referential integrity in the CSV data")
print("=" * 64)
con = duckdb.connect()
for t in sqlcols:
    con.execute(f"CREATE TABLE {t} AS "
                f"SELECT * FROM read_csv_auto('{CSV_DIR}/{t}.csv', header=true)")
    n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"  {t:<20}{n:>8,} rows")

print()
FKS = [
    ("airports.country_id -> countries", "airports", "country_id", "countries", "country_id"),
    ("airlines.country_id -> countries", "airlines", "country_id", "countries", "country_id"),
    ("flight_routes.src_iata -> airports", "flight_routes", "src_iata", "airports", "iata"),
    ("flight_routes.dst_iata -> airports", "flight_routes", "dst_iata", "airports", "iata"),
    ("airline_airports.airline_id -> airlines", "airline_airports", "airline_id", "airlines", "airline_id"),
    ("airline_airports.iata -> airports", "airline_airports", "iata", "airports", "iata"),
]
for label, ct, ck, pt, pk in FKS:
    n = con.execute(f"SELECT count(*) FROM {ct} c LEFT JOIN {pt} p "
                    f"ON c.{ck}=p.{pk} WHERE c.{ck} IS NOT NULL "
                    f"AND p.{pk} IS NULL").fetchone()[0]
    if n:
        errors.append(f"{label}: {n} rows would violate the FK constraint")
    print(f"  {'OK  ' if n == 0 else 'FAIL'} {label:<42}{n}")

print()
PKS = [("countries", "country_id"), ("airports", "iata"),
       ("airlines", "airline_id"), ("flight_routes", "pair_id"),
       ("airline_airports", "serves_id")]
for t, k in PKS:
    tot, dis = con.execute(f"SELECT count(*), count(DISTINCT {k}) FROM {t}").fetchone()
    if tot != dis:
        errors.append(f"{t}.{k} is not unique ({tot-dis} duplicates)")
    print(f"  {'OK  ' if tot == dis else 'FAIL'} PK {t}.{k:<28}{tot-dis} duplicates")

# ----------------------------------------------------- 3. schema.json check
print()
print("=" * 64)
print("3. schema.json against the tables")
print("=" * 64)
S = json.load(open(SCHEMA))
cat = S["catalog"][0]
print(f"  catalog: {cat['name']} ({cat['type']}) -> {cat['jdbc']['jdbcUri']}")
print()

node_ids = {}
for n in S["node"]:
    ds = n["dataSourceGroup"]["externalDataSource"]
    t = ds["table"]
    if t not in sqlcols:
        errors.append(f"node {n['label']}: table air.{t} not created by the SQL")
        print(f"  FAIL {n['label']:<12} unknown table {t}")
        continue
    node_ids[n["label"]] = [c["name"] for c in n["id"]]
    missing = [f["name"] for f in n["id"] + n["attribute"]
               if f["name"] not in sqlcols[t]]
    if missing:
        errors.append(f"node {n['label']}: columns {missing} not in air.{t}")
    attrs = {f["name"] for f in n["attribute"]}
    for c in node_ids[n["label"]]:
        if c not in attrs:
            warnings.append(f"node {n['label']}: id '{c}' not in attribute[], "
                            f"so you cannot RETURN it as a property")
    print(f"  {'OK  ' if not missing else 'FAIL'} {n['label']:<12} air.{t:<18}"
          f"id={node_ids[n['label']]}")

print()
for e in S["edge"]:
    ds = e["dataSourceGroup"]["externalDataSource"]
    t = ds["table"]
    if t not in sqlcols:
        errors.append(f"edge {e['label']}: table air.{t} not created by the SQL")
        continue
    fields = e["id"] + e["fromKey"] + e["toKey"] + e["attribute"]
    missing = [f["name"] for f in fields if f["name"] not in sqlcols[t]]
    if missing:
        errors.append(f"edge {e['label']}: columns {missing} not in air.{t}")
    for side, key in (("fromNodeLabel", "fromKey"), ("toNodeLabel", "toKey")):
        lbl = e[side]
        if lbl not in node_ids:
            errors.append(f"edge {e['label']}: unknown node label '{lbl}'")
        elif len(e[key]) != len(node_ids[lbl]):
            errors.append(f"edge {e['label']}: {key} arity {len(e[key])} "
                          f"!= {lbl} id arity {len(node_ids[lbl])}")
    idc = e["id"][0]["name"]
    tot, dis = con.execute(f"SELECT count(*), count(DISTINCT {idc}) "
                           f"FROM {t}").fetchone()
    null_filter = bool(ds.get("enableNullFilter"))
    nulls = 0
    for k in (e["fromKey"][0]["name"], e["toKey"][0]["name"]):
        nulls += con.execute(f"SELECT count(*) FROM {t} WHERE {k} IS NULL").fetchone()[0]
    if nulls and not null_filter:
        errors.append(f"edge {e['label']}: {nulls} NULL endpoint keys and "
                      f"enableNullFilter is not set")
    elif nulls:
        warnings.append(f"edge {e['label']}: {nulls} NULL endpoint keys "
                        f"dropped by enableNullFilter (expected)")
    if tot != dis:
        errors.append(f"edge {e['label']}: id {idc} not unique")
    print(f"  {'OK  ' if not missing else 'FAIL'} {e['label']:<18}"
          f"{e['fromNodeLabel']} -> {e['toNodeLabel']:<10}{tot:>8,} edges")

con.close()
print()
for w in warnings:
    print(f"WARN  {w}")
for x in errors:
    print(f"ERROR {x}")
print()
if errors:
    print(f"FAILED — {len(errors)} error(s). Fix before running docker compose.")
    sys.exit(1)
print("ALL CHECKS PASSED — safe to run: docker compose up -d")
