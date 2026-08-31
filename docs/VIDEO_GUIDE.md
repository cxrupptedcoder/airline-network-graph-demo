# Video Guide

Structured to mirror the [P2P Payment Fraud Detection demo](https://www.youtube.com/watch?v=9QMZJMxZpQA)
beat for beat, because that video is the house format. Same sections, same UI
features, same order:

| Their video | Your video |
|---|---|
| Docker setup | Docker setup |
| Log in | Log in |
| Upload `fraud_iceberg.json` | Upload `schema.json` |
| Gremlin queries + node expansion | Gremlin queries + node expansion |
| Cypher pattern matching + algorithm | Cypher shortest path + algorithm |
| Visualize tool | Visualize tool |
| Build a Dashboard tile | Build a Dashboard tile |

**Target: 12–13 minutes.** (Trim with the short version in Section 2 and by cutting Section 9 if you need to land under 11.) Do `SETUP.md` first — this guide assumes everything
is installed and you've already done one full practice run.

---

## The golden rules

1. **Never type a query on camera.** Keep them in a scratch file and paste.
   Typos cost whole takes.
2. **Run every query once before recording.** Cold cache turns 2 seconds into 20.
3. **Browser at 125–150% zoom, terminal at 18pt.** Default sizes are unreadable
   on a phone.
4. **`docker compose down --volumes` between takes** so the schema upload beat
   is real rather than pre-loaded.

---

# SECTION 1 — Cold open (0:00–0:35)

**Screen:** `img/03_headline_route.png` full frame.

> "Nepal has no direct flights from North America. So if you're in Seattle and
> you need to get to Kathmandu — how?
>
> Two flights. Seattle to Dubai, Dubai to Kathmandu.
>
> Nothing in the database says that. The database only knows about individual
> flights, thirty-seven thousand of them. That route had to be found.
>
> I'm going to show you how, using PuppyGraph on top of an ordinary PostgreSQL
> database — with no ETL and no data copied anywhere."

Hold three seconds on the image before speaking.

---

# SECTION 2 — Title, and why this matters (0:35–2:00)

This is the section most student demos skip, and it's the one that decides
whether anyone keeps watching. You've shown a neat trick. Now say why a company
would pay for it.

**Screen:** title card for 4 seconds, then `img/01_world_routes.png` underneath
the narration.

### Title card

```
        GLOBAL AIRLINE ROUTE NETWORK ANALYSIS

     Zero-ETL graph queries on PostgreSQL with PuppyGraph

           6,072 airports  ·  37,041 connections
```

Use the same dark background as the images (`#0B0E14`) so the cut to
`img/01_world_routes.png` is seamless. White heading, teal (`#3FD0C9`) subtitle.

### The script (~85 seconds)

> "This is the world's scheduled flight network — six thousand airports,
> thirty-seven thousand nonstop connections — sitting in an ordinary PostgreSQL
> database.
>
> Here's why anyone would care about querying it as a graph.
>
> When a booking site offers you a route with two stops, that's this exact
> query — a shortest path through a network. Nobody stored 'Seattle to
> Kathmandu via Dubai' in a table. It gets found, every time you search.
>
> Airlines ask a harder version: if we open one new route, how many new
> connections does that create for our passengers? One new edge can unlock
> hundreds of new paths.
>
> Governments ask a version with real money attached. The US Essential Air
> Service program subsidizes flights to towns that would otherwise have none —
> and working out which routes are load-bearing is exactly the analysis at the
> end of this video.
>
> And epidemiologists model outbreaks on this network, because a virus doesn't
> travel by geography. It travels by flight route.
>
> Four industries, one query shape. Swap airports for bank accounts and you
> have fraud detection. Swap them for servers and permissions and you have a
> cloud security graph. Swap them for software packages and it's supply-chain
> risk.
>
> What none of those organizations want is a second database. Their data is
> already in a warehouse, it changes constantly, and copying it somewhere else
> to ask graph questions means maintaining a pipeline forever and living with
> stale answers.
>
> So — no ETL, nothing copied. Let me show you."

### Short version (~35 seconds), if you're running long

> "This is the world's flight network sitting in an ordinary PostgreSQL
> database. Every time a booking site offers you a two-stop route, that's this
> query — a shortest path through a network that nobody stored.
>
> Airlines use it for route planning. Governments use it to decide which small
> airports to subsidize. Epidemiologists use it to model how outbreaks spread,
> because a virus travels by flight route, not by geography.
>
> And the same query shape works on bank accounts, cloud permissions, or
> software dependencies. What nobody wants is a second database to run it in.
>
> No ETL, nothing copied. Here's how."

### Delivery notes

- **Slow down here.** This is the only part of the video where you're making an
  argument rather than demonstrating. Rushing it makes it sound like a
  disclaimer you're reading.
- **Land on "no ETL, nothing copied."** That's PuppyGraph's whole positioning,
  and it's the sentence the rest of the video proves.
- **The Essential Air Service line is your credibility beat.** It's a real US
  federal program, it's genuinely the analysis in Section 10, and almost nobody
  making a flight demo knows about it.
- Don't oversell the epidemiology one. "Epidemiologists model outbreaks on this
  network" is true and sufficient. Don't claim you're doing disease modelling.

### Adapting for a different audience

| If your audience is | Lead with |
|---|---|
| PuppyGraph's customers / sales | The "four industries, one query shape" line — move it earlier |
| Engineers | The booking-site line, then straight to the SQL problem |
| A school or general audience | The Kathmandu route, then Essential Air Service |
| Your manager / an internship review | Keep it as written — it shows you understand the product, not just the tool |

---

# SECTION 3 — Environment setup (2:00–3:10)

**Screen:** terminal, in the project folder.

> "Everything runs in Docker. Two containers — PostgreSQL holding the data, and
> PuppyGraph on top of it."

Show `docker-compose.yaml` briefly, then:

```bash
python3 validate.py
```

> "First a pre-flight check. This confirms the SQL, the CSV data, and the graph
> model all agree — before any container starts. It caught two real bugs when I
> built this: a blank primary key, and two airlines whose country field
> contained corrupted source data."

```bash
docker compose up -d
```

> "One command brings up the whole stack."

```bash
docker compose ps
```

**Note on the video you watched:** the fraud demo uses a plain `docker run`
with a `--rm` flag, which deletes the container when it stops. This project
uses Docker Compose because it has to start PostgreSQL too. Same idea, one
extra service. Worth one sentence on camera — it shows you understand the
difference.

**Timing:** Postgres needs 30–40 seconds to load on first boot. Either say
"this is loading about seventy thousand rows" and wait, or cut. Don't ad-lib
over dead air.

---

# SECTION 4 — Show the plain tables (3:10–4:10)

**This is the most important 60 seconds in the video.** Everything after it
only lands if the audience believes the data is ordinary.

```bash
docker exec -it postgres psql -U postgres -d flightdb
```

```sql
\dt air.*
```

> "Five tables. Airports, airlines, countries, the routes between airports, and
> which airlines serve which airports."

```sql
SELECT * FROM air.flight_routes WHERE src_iata = 'SEA' LIMIT 5;
```

> "Each row is one nonstop connection. Origin, destination, distance, which
> airlines fly it.
>
> Now notice what is **not** here. There's no table of multi-leg itineraries.
> No graph. No nodes, no edges. This is a plain relational database — the kind
> any airline or travel company already has."

```sql
\q
```

---

# SECTION 5 — Log in and upload the schema (4:10–5:25)

**Screen:** browser at `http://localhost:8081`.

### Exact clicks

1. Username `puppygraph`, password `puppygraph123` → **Log In**
2. You land on the **Schema** page
3. Find the **Upload Graph Schema JSON** block
4. Click **Choose File** → select `schema.json` from the project folder
5. Click **Upload**
6. The visual schema map renders automatically — pause and let it show

> "Instead of designing the graph by hand in the UI, I upload a JSON file that
> maps the tables to a graph.
>
> Three node types — Airport, Country, Airline. Four edge types. The big one is
> FLIES_TO, which reads the flight_routes table: it runs from the airport in
> the src_iata column to the airport in dst_iata.
>
> And this is the part that matters: **nothing was copied.** No import job ran.
> There's no second database. Postgres still has the exact same five tables it
> had a minute ago. PuppyGraph is only reading them differently."

### Optional 20-second beat (strong if you have room)

Open `schema.json` in an editor and point at `LOCATED_IN`:

> "This edge reads from the airports table — the same table that's already the
> Airport node. The same rows are serving as both nodes and edges. If the graph
> were a copy of my data, doing that would cost me double. It costs nothing."

---

# SECTION 6 — Gremlin queries and visual exploration (5:25–7:55)

**Screen:** click **Query** in the left sidebar → **Gremlin Console** tab.

The fraud video leads with Gremlin and leans hard on right-click expansion.
Do the same — it's the most visually interesting part of the whole video.

### Query 1 — the radiating cluster

```groovy
g.V().hasLabel('Airport').has('iata','SEA').out('FLIES_TO')
```

> "Every nonstop destination from Seattle. Ninety airports."

**Let the graph render.** One node at the centre, ninety radiating out. This is
your equivalent of the fraud video's cluster of 243 nodes.

**Switch layouts** using the layout selector — show **Radial**, then **Force**.

> "The visualization has a few layouts. Radial is good for showing one hub;
> force-directed is better for seeing overall structure."

### Query 2 — one node, then expand it

```groovy
g.V().hasLabel('Airport').has('iata','KTM')
```

> "Here's Kathmandu on its own."

**Now the key interaction:** right-click the node → **Expand with all Edge
Labels**.

> "Right-click, expand with all edge labels, and it traverses outward — showing
> everywhere Kathmandu connects, which country it's in, and which airlines
> serve it."

**Expand one more node** from what appears — pick a neighbouring airport and
right-click → expand again.

> "You can keep walking outward from any node. This is how you'd explore a
> network you don't already know."

### Query 3 — the path

```groovy
g.V().hasLabel('Airport').has('iata','SEA')
 .out('FLIES_TO').out('FLIES_TO')
 .has('iata','KTM').path()
```

> "And here's the actual route — Seattle, Dubai, Kathmandu — as a path."

**Heads up:** this returns **two** paths, not one — `SEA → DXB → KTM` and
`SEA → ICN → KTM` (Seoul Incheon). That's better, not worse. Say:

> "Actually there are two two-flight routes — one through Dubai, one through
> Seoul. The graph found both."

Switch to **Vertical** layout to show the chains cleanly.

---

# SECTION 7 — Cypher: pattern matching and algorithms (7:55–10:10)

**Screen:** click the **Cypher Console** tab.

> "PuppyGraph speaks both Gremlin and Cypher. Cypher reads more like a
> sentence, so I'll use it for the analysis."

### Query 4 — shortest path, the headline

```cypher
USING enableCypherEngineProperties 'true'
MATCH (a:Airport {iata: 'SEA'}), (b:Airport {iata: 'KTM'}),
      path = shortestPath((a)-[:FLIES_TO*..6]->(b))
RETURN [n IN nodes(path) | n.city + ' (' + n.iata + ')'] AS route,
       length(path) AS flights
```

> "Read it out loud and it's an English sentence. Find an airport with the code
> SEA, find one with KTM, give me the shortest chain of FLIES_TO connections
> between them, up to six.
>
> Two flights, via Dubai.
>
> The important part is that `*..6`. I never told it the answer was two — it
> searched until it found the shortest one."

**Now change `KTM` to `USH` and re-run.**

> "Ushuaia, Argentina — the southernmost city in the world. Three flights, via
> Dallas and Buenos Aires. Same query. I changed three letters.
>
> In SQL, going from two flights to three means rewriting the query with
> another join. That's the difference."

### Query 5 — the reach expansion

```cypher
MATCH (sea:Airport {iata: 'SEA'})-[:FLIES_TO*1..2]->(d:Airport)
RETURN count(DISTINCT d) AS reachable
```

Run it, then change `*1..2` → `*1..3` → `*1..4`, running each time.

> "One flight, ninety-one airports. Two flights, twelve hundred. Three flights,
> twenty-seven hundred. Then it flattens out.
>
> That's the small-world effect — a handful of huge hubs connect everything, so
> almost the entire network sits within three or four hops of anywhere."

Cut to `img/04_reach_expansion.png` on that last line.

### Query 6 — the algorithm

```cypher
CALL algo.paral.pagerank({
    labels: ['Airport'],
    relationshipTypes: ['FLIES_TO'],
    maxIterations: 40,
    dampingFactor: 0.85
}) YIELD id, score
RETURN id, score ORDER BY score DESC LIMIT 15
```

> "PuppyGraph has graph algorithms built in. PageRank — the same algorithm
> Google used to rank web pages — asks not how many connections an airport has,
> but how much of the world's travel routes *through* it.
>
> Atlanta comes first. Frankfurt, which has the most raw connections of any
> airport on Earth, drops to eighth. Denver is fourteenth by connection count
> but fourth by PageRank.
>
> They answer different questions. Connection count says 'most destinations
> served.' PageRank says 'most central to global circulation.'"

**Don't claim PageRank is "better."** An aviation person knows Frankfurt is the
bigger international hub, and overclaiming loses them.

---

# SECTION 8 — The Visualize tool (10:10–11:10)

**Screen:** click **Visualize** in the left sidebar.

This is the macro view of the whole dataset, and it's the section most student
demos skip. The fraud video uses it — so should you.

### Exact steps

1. Click **Visualize** in the left sidebar
2. Use the **search box** to find a specific node — search `SEA`
3. **Zoom in** on it (scroll or pinch)
4. **Click the node** to highlight all its connected edges
5. **Right-click the node** to view its properties — label, IATA code, city,
   coordinates

> "The Visualize tool gives a view of the whole graph at once. I can search for
> a specific airport, click it to light up everything it connects to, and
> right-click to read its properties straight out of the Postgres table."

Then search `KTM`, click it, and contrast:

> "And here's Kathmandu — far sparser. You can see the difference between a
> mega-hub and a regional airport just by looking."

---

# SECTION 9 — Build a Dashboard (11:10–12:25)

**Screen:** click **Dashboard** in the left sidebar.

The dashboard defaults to vertex/edge counts and sample tables.

### Exact steps

1. Click **Dashboard** in the left sidebar
2. Click the **+** icon at the bottom
3. Click **Edit**
4. **Title:** `Airports with a Single Connection`
5. **Query Input:** paste this Cypher:

```cypher
USING enableCypherEngineProperties 'true'
MATCH (a:Airport)-[:FLIES_TO]-(other:Airport)
WITH a, count(DISTINCT other) AS links
WHERE links = 1
RETURN a.iata, a.city, a.country_id
ORDER BY a.country_id LIMIT 50
```

6. **Display Type:** select **Table** — this one is a list, not a network
7. Click **Submit**

Add a second tile the same way, this time as a graph:

- **Title:** `Seattle Direct Routes`
- **Query Input:** `g.V().hasLabel('Airport').has('iata','SEA').out('FLIES_TO')`
- **Display Type:** **Graph**, layout **Radial**
- **Submit**

> "Queries worth keeping become dashboard tiles. This is a live panel — it
> re-runs against Postgres every time you load it, so it's never stale."

---

# SECTION 10 — The finding, and the close (12:25–13:25)

**Screen:** `img/07_fragile_airports.png`.

> "One last thing, and it's the result that surprised me most.
>
> If the busiest airport in the world shut down — Frankfurt, 477 connections —
> how much of the network breaks?
>
> Almost none. Exactly one airport gets cut off, because every mega-hub has an
> alternative.
>
> The fragility is somewhere else. **747 airports have exactly one connection.**
> Ayacucho in Peru only reaches Lima. Basco in the Philippines only reaches
> Manila. Cancel that single route and the town leaves the network entirely.
>
> If you're doing resilience analysis, you should be looking at the edges, not
> the hubs. That's the sort of thing you only see when you model it as a graph.
>
> Five ordinary Postgres tables. One schema file. No ETL, no second database,
> nothing copied. The repo is linked below — it's two commands to run it
> yourself."

---

# Scratch file — paste-ready queries

Keep these in a text file before you record, in this order.

```groovy
// Gremlin 1 — Seattle's direct routes
g.V().hasLabel('Airport').has('iata','SEA').out('FLIES_TO')

// Gremlin 2 — one node to expand
g.V().hasLabel('Airport').has('iata','KTM')

// Gremlin 3 — the two-hop path
g.V().hasLabel('Airport').has('iata','SEA').out('FLIES_TO').out('FLIES_TO').has('iata','KTM').path()
```

```cypher
// Cypher 1 — sanity check
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC

// Cypher 2 — shortest path
USING enableCypherEngineProperties 'true'
MATCH (a:Airport {iata: 'SEA'}), (b:Airport {iata: 'KTM'}),
      path = shortestPath((a)-[:FLIES_TO*..6]->(b))
RETURN [n IN nodes(path) | n.city + ' (' + n.iata + ')'] AS route, length(path) AS flights

// Cypher 3 — reach expansion (change 2 -> 3 -> 4)
MATCH (sea:Airport {iata: 'SEA'})-[:FLIES_TO*1..2]->(d:Airport)
RETURN count(DISTINCT d) AS reachable

// Cypher 4 — PageRank
CALL algo.paral.pagerank({labels:['Airport'], relationshipTypes:['FLIES_TO'],
    maxIterations:40, dampingFactor:0.85}) YIELD id, score
RETURN id, score ORDER BY score DESC LIMIT 15

// Cypher 5 — dashboard tile
USING enableCypherEngineProperties 'true'
MATCH (a:Airport)-[:FLIES_TO]-(other:Airport)
WITH a, count(DISTINCT other) AS links
WHERE links = 1
RETURN a.iata, a.city, a.country_id ORDER BY a.country_id LIMIT 50
```

---

# Troubleshooting while recording

| Problem | Cause | Fix |
|---|---|---|
| Schema upload fails | Postgres still loading | `docker compose logs postgres`, wait for "ready to accept connections" |
| Properties come back empty | Missing the `USING` line | Add `USING enableCypherEngineProperties 'true'` |
| First query takes 20 seconds | Cold cache | Run everything once before recording |
| Graph view is an unreadable hairball | Too many nodes returned | Add `LIMIT`, or query a single path |
| Right-click menu doesn't appear | Clicked empty canvas | Click precisely on the node circle |
| Port 8081 in use | Old container still running | `docker compose down --remove-orphans` |
| Everything is wrong | — | `docker compose down --volumes --remove-orphans`, then `up -d` |

---

# Publishing

## Choosing a title

A demo title has two jobs: say what the thing is, and give someone a reason to
click. Most student demos only do the first.

### Recommended

**Global Airline Route Network Analysis with PuppyGraph — Zero-ETL Graph Queries on PostgreSQL**

This is the safe pick and the one to use if the video goes on PuppyGraph's demo
page. It matches their existing naming exactly — compare *"P2P Payment Platform
Fraud Detection"* and *"Telecom Customer 360 Graph Demo"*. Product name in the
title, "zero-ETL" as the hook, data store named.

### Alternatives, by what you want to optimise for

| Title | Best for | Trade-off |
|---|---|---|
| *Global Airline Route Network Analysis with PuppyGraph — Zero-ETL Graph Queries on PostgreSQL* | Their demo page | Descriptive, not clicky |
| *Finding Routes, Hubs, and Weak Points in the World's Flight Network* | YouTube search | Doesn't say PuppyGraph |
| *What Happens if the World's Busiest Airport Closes? Graph Analysis of 37,000 Flight Routes* | Clicks | Buries the product |
| *Seattle to Kathmandu in Two Flights: Graph Queries on 6,000 Airports with PuppyGraph* | Balance of both | Slightly long |

**My pick if you get to choose freely:** the last one. It leads with the
concrete result, names the product, and the numbers signal it's a real dataset
rather than a toy.

**If your manager is choosing:** use the first. Matching their house naming is
worth more than clicks on an internal demo.

### Rules to follow either way

- **Put "PuppyGraph" in the title.** It's the point of the video.
- **Include a number.** "37,041 routes" or "6,000 airports" signals real data.
- **Don't write "Demo" twice.** "Airline Demo Video Demo" happens more than
  you'd think.
- **Keep it under about 70 characters** if you care about it not being cut off
  in search results.

## Thumbnail

Use **`img/03_headline_route.png`** — the Seattle → Kathmandu polar arc. It's
the most striking image in the set and it poses a question.

Add three or four words of large text in the upper-left dead space, where the
map is empty:

- **"2 FLIGHTS"** (biggest text, teal)
- **"Seattle → Kathmandu"** (smaller, white, underneath)

Keep it to that. Thumbnails with a paragraph on them are unreadable at phone
size. Test yours by shrinking it to 200 px wide — if you can't read it, cut words.

## Description

Matches the style of their existing demo pages:

> In this demo, we model the world's scheduled flight network as a graph to
> answer routing and resilience questions that are difficult to express in SQL.
> Using 6,072 airports and 37,041 nonstop connections stored in PostgreSQL,
> PuppyGraph enables you to:
>
> - Find multi-leg itineraries between airports with no direct service
> - Measure how much of the world becomes reachable with each additional flight
> - Rank hub importance by PageRank rather than raw connection count
> - Identify the airports a single cancelled route would isolate
>
> We find that removing the world's busiest airport disconnects only one other
> airport, while 747 small airports depend on a single route — inverting the
> usual intuition about where network risk lives.
>
> The demo uses open data from OpenFlights and walks through how to:
>
> - Use Docker Compose to launch PostgreSQL and PuppyGraph
> - Upload the graph model into PuppyGraph
> - Run interactive Gremlin and Cypher queries
> - Explore results with the visualization tool and build a dashboard
>
> All services are spun up using Docker Compose, and setup requires only
> Docker, Python 3, and Docker Compose. No ETL or data duplication required.
>
> GitHub: [your repo link]
> Data: OpenFlights (https://openflights.org), Open Database License

## Chapters

YouTube auto-generates chapter markers from timestamps in the description.
Paste these and adjust to your final cut:

```
0:00  Seattle to Kathmandu in two flights
0:35  Why route networks are a graph problem
2:00  Starting PostgreSQL and PuppyGraph
3:10  The data: five ordinary tables
4:10  Uploading the graph model
5:25  Exploring with Gremlin
7:55  Shortest paths and PageRank in Cypher
10:10 The Visualize tool
11:10 Building a dashboard
12:25 What happens if a mega-hub closes
```

**Credit OpenFlights.** The data is ODbL — attribution is a licence condition,
not a courtesy.
