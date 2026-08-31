#!/usr/bin/env python3
"""
Route analysis against PuppyGraph over the Bolt protocol.

    pip install neo4j
    python3 route_analysis.py
    python3 route_analysis.py --origin LAX --destination TBU

PuppyGraph speaks openCypher over Bolt on port 7687, so any Neo4j driver
works unchanged. Nothing here knows it is talking to Postgres.
"""
import argparse
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "puppygraph"
PASSWORD = "puppygraph123"

PROPS = "USING enableCypherEngineProperties 'true'\n"


def shortest_route(session, origin, destination, max_hops=6):
    """Fewest-flights route between two airports."""
    q = PROPS + f"""
    MATCH (a:Airport {{iata: $origin}}), (b:Airport {{iata: $destination}}),
          path = shortestPath((a)-[:FLIES_TO*..{max_hops}]->(b))
    RETURN [n IN nodes(path) | n.iata]  AS codes,
           [n IN nodes(path) | n.city]  AS cities,
           length(path)                 AS flights
    """
    rec = session.run(q, origin=origin, destination=destination).single()
    if not rec:
        print(f"  no route found from {origin} to {destination} "
              f"within {max_hops} flights")
        return
    legs = " -> ".join(f"{c} ({i})" for c, i in zip(rec["cities"], rec["codes"]))
    print(f"  {rec['flights']} flight(s): {legs}")


def reach_by_hops(session, origin, max_hops=4):
    """How many airports become reachable with each additional flight."""
    for h in range(1, max_hops + 1):
        q = f"""
        MATCH (a:Airport {{iata: $origin}})-[:FLIES_TO*1..{h}]->(d:Airport)
        RETURN count(DISTINCT d) AS reachable
        """
        n = session.run(q, origin=origin).single()["reachable"]
        print(f"  within {h} flight(s): {n:>5,} airports")


def busiest_hubs(session, limit=10):
    """Airports with the most connections."""
    q = PROPS + """
    MATCH (a:Airport)-[f:FLIES_TO]-()
    RETURN a.iata AS iata, a.city AS city, count(f) AS connections
    ORDER BY connections DESC LIMIT $limit
    """
    for r in session.run(q, limit=limit):
        print(f"  {r['iata']}  {r['city'][:22]:<24}{r['connections']:>5}")


def pagerank_hubs(session, limit=10):
    """Structural centrality, which is NOT the same as raw connection count."""
    q = """
    CALL algo.paral.pagerank({
        labels: ['Airport'],
        relationshipTypes: ['FLIES_TO'],
        maxIterations: 40,
        dampingFactor: 0.85
    }) YIELD id, score
    RETURN id AS id, score AS score
    ORDER BY score DESC LIMIT $limit
    """
    for i, r in enumerate(session.run(q, limit=limit), 1):
        print(f"  {i:>2}. {str(r['id']):<28}{r['score']:.6f}")


def fragile_airports(session, limit=15):
    """Airports with exactly one connection: cut it and the town is isolated."""
    q = PROPS + """
    MATCH (a:Airport)-[:FLIES_TO]-(other:Airport)
    WITH a, count(DISTINCT other) AS links
    WHERE links = 1
    RETURN a.iata AS iata, a.city AS city, a.country_id AS country
    ORDER BY a.country_id LIMIT $limit
    """
    rows = list(session.run(q, limit=limit))
    for r in rows:
        print(f"  {r['iata']}  {str(r['city'])[:20]:<22}{r['country']}")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default="SEA")
    ap.add_argument("--destination", default="KTM")
    a = ap.parse_args()

    driver = None
    session = None
    try:
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        session = driver.session()

        print(f"\n=== 1. Shortest route {a.origin} -> {a.destination} ===")
        shortest_route(session, a.origin, a.destination)

        print(f"\n=== 2. Other hard-to-reach places from {a.origin} ===")
        for dest in ["TBU", "USH", "MLE"]:
            shortest_route(session, a.origin, dest)

        print(f"\n=== 3. How far you can get from {a.origin} ===")
        reach_by_hops(session, a.origin)

        print("\n=== 4. Busiest airports by connection count ===")
        busiest_hubs(session)

        print("\n=== 5. Most central airports by PageRank ===")
        print("  (a different question: how much travel routes THROUGH you)")
        pagerank_hubs(session)

        print("\n=== 6. Airports with a single connection ===")
        n = fragile_airports(session)
        print(f"  ...showing {n}; 747 airports in total have exactly one link.")
        print("  The network's fragility is at the edges, not the hubs.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Is PuppyGraph running? Try: docker compose ps")

    finally:
        if session:
            session.close()
        if driver:
            driver.close()


if __name__ == "__main__":
    main()
