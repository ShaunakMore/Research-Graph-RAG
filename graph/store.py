from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
  os.getenv("NEO4J_URI"), #type:ignore
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")) #type:ignore
)

def add_to_graph(s, type: str, name: str, unique_names: set, associated_method: str = "", paper: str = "", status: str = "", statement: str ="", description: str = ""):
    if type.lower() == "method" and status.lower() == "proposed" and name.lower() not in unique_names:
        m = name
        s.run("""
            MERGE (x:Method {name:$m})
            MERGE (p:Paper {name:$p})
            MERGE (p)-[:PROPOSES]->(x)
            """, m=m, p=paper)
        unique_names.add(m.lower())
    
    elif type.lower() == "dataset" and associated_method.lower() in unique_names:
        d = name
        m = associated_method
        s.run("""
            MERGE (d:Dataset {name:$d})
            MERGE (x:Method {name:$m})
            MERGE (x)-[:EVALUATED_ON]->(d)
            """, d=d, m=m)
    elif type.lower() == "metric" and associated_method.lower() in unique_names:
        met = name
        mtd = associated_method
        s.run("""
            MERGE (m:Metric {name:$met})
            MERGE (x:Method {name:$mtd})
            MERGE (x)-[:MEASURED_BY]->(m)
            """, met=met, mtd=mtd)

    elif type.lower() == "claim" and associated_method.lower() in unique_names:
        clm = statement
        mtd = associated_method
        s.run("""
            MERGE (c:Claim {name:$clm})
            MERGE (x:Method {name:$mtd})
            MERGE (x)-[:ACHIEVED]->(C)
            """, clm=clm, mtd=mtd)

    elif type.lower() == "limitation" and associated_method.lower() in unique_names:
        lim = description
        mtd = associated_method
        s.run("""
            MERGE (l:Limitation {text:$lim})
            MERGE (m:Method {name:$mtd})
            MERGE (m)-[:HAS_LIMITATION]->(l)
            """, lim=lim, mtd=mtd)
    
    
    
def add_knowledge(user_id, paper_id, entities_json, unique_methods):
    """
    user_id: The unique ID of the user (from Auth)
    paper_id: The Title or DOI of the paper
    entities_json: The list of entities from the LLM
    unique_methods: A set to keep track of proposed methods across the whole paper
    """
    
    entities = entities_json.get("entities", [])
    if not entities:
        return

    with driver.session() as session:
        # 1. Ensure the User exists and OWNS this Paper
        # We include userId in the Paper MERGE to ensure papers with the same title 
        # but different users remain separate.
        session.run("""
            MERGE (u:User {id: $uid})
            MERGE (p:Paper {name: $pname, userId: $uid})
            MERGE (u)-[:OWNS]->(p)
        """, uid=user_id, pname=paper_id)

        # 2. FIRST PASS: Create all 'Proposed' Methods
        for ent in entities:
            if ent.get("type") == "METHOD" and ent.get("status") == "PROPOSED":
                name = ent.get("name", "Unknown Method").strip()
                # KEY CHANGE: MERGE on name AND userId so methods aren't shared between users
                session.run("""
                    MATCH (p:Paper {name: $paper_id, userId: $uid})
                    MERGE (m:Method {name: $name, userId: $uid})
                    MERGE (p)-[:PROPOSES]->(m)
                """, name=name, paper_id=paper_id, uid=user_id)
                
                unique_methods.add(name.lower())

        # 3. SECOND PASS: Create everything else
        for ent in entities:
            e_type = ent.get("type", "").upper()
            target_method = ent.get("associated_method", "").strip()
            
            parent_label = "Method" if target_method.lower() in unique_methods else "Paper"
            parent_name = target_method if parent_label == "Method" else paper_id
            
            # Helper to run the dynamic MERGE
            # Note: We use f-strings for labels but PARAMS for values to prevent injection
            def run_upsert(label, rel, prop_name, prop_val):
                query = f"""
                    MATCH (parent:{parent_label} {{name: $parent_name, userId: $uid}})
                    MERGE (child:{label} {{{prop_name}: $val, userId: $uid}})
                    MERGE (parent)-[:{rel}]->(child)
                """
                session.run(query, parent_name=parent_name, val=prop_val, uid=user_id)

            if e_type == "DATASET":
                run_upsert("Dataset", "EVALUATED_ON", "name", ent.get("name"))
            elif e_type == "METRIC":
                run_upsert("Metric", "MEASURED_BY", "name", ent.get("name"))
            elif e_type == "CLAIM":
                run_upsert("Claim", "ACHIEVED", "text", ent.get("statement"))
            elif e_type == "LIMITATION":
                run_upsert("Limitation", "HAS_LIMITATION", "text", ent.get("description"))
