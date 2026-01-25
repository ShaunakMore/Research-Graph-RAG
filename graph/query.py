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
    for i, rows in enumerate(results):
        for res in rows:
            paper = res.get("paper", "UNKNOWN")
            method = res.get("method", "")
            
            # This ensures we don't say "METHOD: " if we fell back to Paper-level data
            method_line = f"METHOD: {method}\n" if method else ""

            for key, value in res.items():
                if key in ["paper", "method"]: continue

                # If the CASE statement returned an empty list for both, show "None Found"
                if isinstance(value, list):
                    joined = ", ".join(value) if value else "None Found"
                else:
                    joined = str(value) if value else "None Found"

                graph_res += f"[GRAPH_{i+1}]\nPAPER: {paper}\n{method_line}{key.upper()}: {joined}\n\n"
    return graph_res


def query_graph(intent, user_id): # Added user_id parameter
    print(f"\nReceived intent: {intent}\n")

    e = intent["entities"]
    t = intent["type"]
    results = []
    if not e:
        return results
        
    for ent in e:
        # ----- STEP 1: Find entity nodes restricted by User ID -----
        paper_query = """
        MATCH (n {userId: $uid})
        WHERE toLower(n.name) CONTAINS toLower($e)
            OR toLower($e) CONTAINS toLower(n.name)

        OPTIONAL MATCH (p:Paper {userId: $uid})-[]->(n)

        RETURN DISTINCT
        coalesce(p.name, n.name) as paper
        LIMIT 1
        """

        with driver.session() as s:
            # Pass uid to the driver
            paper_res = s.run(paper_query, e=ent, uid=user_id).data()

        if not paper_res:
            continue

        paper = paper_res[0]["paper"]
        print(f"\nResolved Paper: {paper}\n")

        # ----- UPDATED QUERIES WITH userId FILTERS -----
        
        # Method Question
        if t == "method":
            q = """
            MATCH (p:Paper {name: $paper, userId: $uid})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method {userId: $uid})
            RETURN p.name as paper, collect(DISTINCT m.name) as methods
            """

        # Dataset Question
        elif t == "dataset":
            q = """
            MATCH (p:Paper {name: $paper, userId: $uid})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method {userId: $uid})
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:EVALUATED_ON]->(d:Dataset {userId: $uid})
            WITH p, m, collect(DISTINCT d.name) as method_datasets
            
            OPTIONAL MATCH (p)-[:EVALUATED_ON]->(pd:Dataset {userId: $uid})
            WITH p, m, method_datasets, collect(DISTINCT pd.name) as paper_datasets
            
            RETURN p.name as paper, coalesce(m.name, "") as method,
                   CASE WHEN size(method_datasets) > 0 THEN method_datasets ELSE paper_datasets END as datasets
            """

        # Metric Question
        elif t == "metric":
            q = """
            MATCH (p:Paper {name: $paper, userId: $uid})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method {userId: $uid})
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:MEASURED_BY]->(met:Metric {userId: $uid})
            WITH p, m, collect(DISTINCT met.name) as method_metrics
            
            OPTIONAL MATCH (p)-[:MEASURED_BY]->(p_met:Metric {userId: $uid})
            WITH p, m, method_metrics, collect(DISTINCT p_met.name) as paper_metrics
            
            RETURN p.name as paper, coalesce(m.name, "") as method,
                   CASE WHEN size(method_metrics) > 0 THEN method_metrics ELSE paper_metrics END as metrics
            """

        # Limitation Question
        elif t == "limitation":
            q = """
            MATCH (p:Paper {name: $paper, userId: $uid})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method {userId: $uid})
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:HAS_LIMITATION]->(l:Limitation {userId: $uid})
            WITH p, m, collect(DISTINCT l.text) as method_limitations
            
            OPTIONAL MATCH (p)-[:HAS_LIMITATION]->(p_l:Limitation {userId: $uid})
            WITH p, m, method_limitations, collect(DISTINCT p_l.text) as paper_limitations
            
            RETURN p.name as paper, coalesce(m.name, "") as method,
                   CASE WHEN size(method_limitations) > 0 THEN method_limitations ELSE paper_limitations END as limitations
            """

        # Claim Question
        elif t in ["claim", "claims"]:
            q = """
            MATCH (p:Paper {name: $paper, userId: $uid})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method {userId: $uid})
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:ACHIEVED]->(c:Claim {userId: $uid})
            WITH p, m, collect(DISTINCT c.text) as method_claims
            
            OPTIONAL MATCH (p)-[:ACHIEVED]->(p_c:Claim {userId: $uid})
            WITH p, m, method_claims, collect(DISTINCT p_c.text) as paper_claims
            
            RETURN p.name as paper, coalesce(m.name, "") as method,
                   CASE WHEN size(method_claims) > 0 THEN method_claims ELSE paper_claims END as claims
            """
        else:
            continue

        with driver.session() as s:
            # Always pass the uid parameter
            results.append(s.run(q, paper=paper, e=ent, uid=user_id).data()) 
    
    return prepare_result(results)