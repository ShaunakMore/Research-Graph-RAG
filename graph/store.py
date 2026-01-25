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
    
    
    
def add_knowledge(paper_id, entities_json, unique_methods):
    """
    paper_id: The Title or DOI of the paper
    entities_json: The list of entities from the LLM
    unique_methods: A set to keep track of proposed methods across the whole paper
    """
    entities = entities_json.get("entities", [])
    if not entities:
        return

    with driver.session() as session:
        # 1. Ensure the Paper node exists
        session.run("MERGE (p:Paper {name: $n})", n=paper_id)

        # 2. FIRST PASS: Create all 'Proposed' Methods
        # We do this first so other entities have an anchor to attach to.
        for ent in entities:
            if ent.get("type") == "METHOD" and ent.get("status") == "PROPOSED":
                name = ent.get("name", "Unknown Method").strip()
                session.run("""
                    MERGE (m:Method {name: $name})
                    WITH m
                    MATCH (p:Paper {name: $paper_id})
                    WHERE toLower(p.name) = toLower($paper_id)
                    MERGE (p)-[:PROPOSES]->(m)
                """, name=name, paper_id=paper_id)
                print(f"\nADDED METHOD {name} TO PAPER {paper_id}\n")
                unique_methods.add(name.lower())

        # 3. SECOND PASS: Create everything else
        for ent in entities:
            e_type = ent.get("type", "").upper()
            target_method = ent.get("associated_method", "").strip()
            
            # Logic: If the method is known, link to Method. 
            # Otherwise, link directly to the Paper as a fallback.
            parent_label = "Method" if target_method.lower() in unique_methods else "Paper"
            parent_name = target_method if parent_label == "Method" else paper_id
            
            if e_type == "DATASET":
                session.run(f"""
                    MERGE (d:Dataset {{name: $name}})
                    WITH d
                    MATCH (parent:{parent_label} {{name: $parent_name}})
                    MERGE (parent)-[:EVALUATED_ON]->(d)
                """, name=ent.get("name"), parent_name=parent_name)
                print(f"\nADDED DATASET {ent.get("name")} TO NODE {parent_name}\n")

            elif e_type == "METRIC":
                session.run(f"""
                    MERGE (met:Metric {{name: $name}})
                    WITH met
                    MATCH (parent:{parent_label} {{name: $parent_name}})
                    MERGE (parent)-[:MEASURED_BY]->(met)
                """, name=ent.get("name"), parent_name=parent_name)
                print(f"\nADDED METRIC {ent.get("name")} TO NODE {parent_name}\n")

            elif e_type == "CLAIM":
                session.run(f"""
                    MERGE (c:Claim {{text: $text}})
                    WITH c
                    MATCH (parent:{parent_label} {{name: $parent_name}})
                    MERGE (parent)-[:ACHIEVED]->(c)
                """, text=ent.get("statement"), parent_name=parent_name)
                print(f"\nADDED CLAIM {ent.get("statement")} TO NODE {parent_name}\n")

            elif e_type == "LIMITATION":
                session.run(f"""
                    MERGE (l:Limitation {{text: $text}})
                    WITH l
                    MATCH (parent:{parent_label} {{name: $parent_name}})
                    MERGE (parent)-[:HAS_LIMITATION]->(l)
                """, text=ent.get("description"), parent_name=parent_name)
                print(f"\nADDED LIMITATION {ent.get("description")} TO NODE {parent_name}\n")
