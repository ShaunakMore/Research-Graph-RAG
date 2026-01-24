from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
load_dotenv()

driver = GraphDatabase.driver(
  os.getenv("NEO4J_URI"), #type:ignore
  auth=(os.getenv("NEO4J_USER"),os.getenv("NEO4J_PASSWORD")) #type:ignore
)

def prepare_result(results):
    graph_res = ""

    for i,rows in enumerate(results):
        for res in rows:
            paper = res.get("paper", "UNKNOWN")

            for key, value in res.items():
                if key == "paper":
                    continue

                joined = ", ".join(value) if value else "None"

                graph_res += f"""
                [GRAPH_{i+1}]PAPER: {paper}
                {key.upper()}: {joined}

                """

    return graph_res


def query_graph(intent):
    print(f"\nRecieved intent: {intent}\n")

    e = intent["entities"]
    t = intent["type"]
    results = []
    if not e:
        return results
    for ent in e:
        # ----- STEP 1: Find entity nodes -----
        
        # print(f"\nChosen Entity: {entity}\n")
        # print(f"\nChosen question type: {t}\n")

        paper_query = """
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($e)
            OR toLower($e) CONTAINS toLower(n.name)

        OPTIONAL MATCH (p:Paper)-[]->(n)

        RETURN DISTINCT
        coalesce(p.name, n.name) as paper
        LIMIT 1
        """

        with driver.session() as s:
            paper_res = s.run(paper_query, e=ent).data()

        if not paper_res:
            continue

        paper = paper_res[0]["paper"]
        print(f"\nResolved Paper: {paper}\n")

        # ----- METHOD QUESTION -----
        if t == "method":

            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)

            RETURN
            p.name as paper,
            collect(DISTINCT m.name) as methods
            """

        # ----- DATASET QUESTION -----
        elif t == "dataset":

            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:USES]->(d:Dataset)

            RETURN
            p.name as paper,
            collect(DISTINCT d.name) as datasets
            """

        # ----- METRIC QUESTION -----
        elif t == "metric":

            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:REPORTS]->(me:Metric)

            RETURN
            p.name as paper,
            collect(DISTINCT me.name) as metrics
            """

        # ----- LIMITATION QUESTION -----
        elif t == "limitation":

            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:HAS_LIMITATION]->(l:Limitation)

            RETURN
            p.name as paper,
            collect(DISTINCT l.text) as limitations
            """

        else:
            continue

        with driver.session() as s:
            results.append(s.run(q, paper=paper).data()) 
    
    return prepare_result(results)