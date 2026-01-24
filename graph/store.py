from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
  os.getenv("NEO4J_URI"), #type:ignore
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")) #type:ignore
)

def normalize_list(items):
    clean = []

    for x in items:
        # Case 1: already string
        if isinstance(x, str):
            clean.append(x)

        # Case 2: dict → take key or value
        elif isinstance(x, dict):
            # take first key-value as string
            for k, v in x.items():
                if isinstance(v, list):
                    clean.append(f"{k}: {', '.join(map(str,v))}")
                else:
                    clean.append(f"{k}: {v}")

        # Case 3: something else
        else:
            clean.append(str(x))

    return clean


def add_knowledge(paper_id, entities):

    with driver.session() as s:

        s.run("MERGE (p:Paper {name:$n})", n=paper_id)

        # ===== METHODS =====
        methods = normalize_list(entities.get("methods", []))

        for m in methods:
            s.run("""
            MERGE (x:Method {name:$m})
            MERGE (p:Paper {name:$p})
            MERGE (p)-[:PROPOSES]->(x)
            """, m=m, p=paper_id)

        # ===== DATASETS =====
        datasets = normalize_list(entities.get("datasets", []))

        for d in datasets:
            s.run("""
            MERGE (d:Dataset {name:$d})
            MERGE (p:Paper {name:$p})
            MERGE (p)-[:USES]->(d)
            """, d=d, p=paper_id)

        # ===== LIMITATIONS =====
        limits = normalize_list(entities.get("limitations", []))

        for l in limits:
            s.run("""
            MERGE (l:Limitation {text:$l})
            MERGE (p:Paper {name:$p})
            MERGE (p)-[:HAS_LIMITATION]->(l)
            """, l=l, p=paper_id)
