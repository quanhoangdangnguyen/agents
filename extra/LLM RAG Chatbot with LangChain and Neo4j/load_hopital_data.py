from neo4j import GraphDatabase
import logging
from pathlib import Path
from retry import retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)

# Connection details
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "123456789")

def check_connection():
    try:
        # The 'with' statement handles closing the driver automatically
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("Connection Successful!")
    except Exception as e:
        print(f"Connection Failed: {e}")

dict_NODES = {
            "Hospital":'hospitals.csv',
            "Payer":"payers.csv",
            "Physician":"physicians.csv",
            "Patient":"patients.csv",
            "Visit":"visits.csv",
            "Review":"reviews.csv"
            }

def _set_uniqueness_constraints(tx, node):
    query = f"""CREATE CONSTRAINT unique_{node} IF NOT EXISTS FOR (n:{node})
        REQUIRE n.id IS UNIQUE;"""
    _ = tx.run(query, {})

@retry(tries=100, delay=10)
def set_constraint() -> None:
    """Load structured hospital CSV data following
    a specific ontology into Neo4j"""

    LOGGER.info("Setting uniqueness constraints on nodes")
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        session=driver.session(database='hopitaldata')
        for node in dict_NODES:
            session.execute_write(_set_uniqueness_constraints, node)

def load_hospital_graph_from_csv() -> None:
    LOGGER.info("Loading hospital nodes")
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Hospital']}' AS row
            MERGE (h:Hospital {{id: toInteger(row.hospital_id),
                                name: row.hospital_name,
                                state_name: row.hospital_state}});
            """
            _ = session.run(query, {})

        LOGGER.info("Loading patient nodes")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Patient']}' AS row
            MERGE (h:Patient {{id: toInteger(row.patient_id),
                                name: row.patient_name,
                                sex: row.patient_sex,
                                dob:date(row.patient_dob),
                                blood_type:row.patient_blood_type
                                }});
            """
            _ = session.run(query, {})

        LOGGER.info("Loading payer nodes")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Payer']}' AS row
            MERGE (h:Payer {{id: toInteger(row.payer_id),
                                name: row.payer_name
                                }});
            """
            _ = session.run(query, {})

        LOGGER.info("Loading physician nodes")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Physician']}' AS row
            MERGE (h:Physician {{id: toInteger(row.physician_id),
                                name: row.physician_name,
                                dob:date(row.physician_dob),
                                grad_year:date(row.physician_grad_year),
                                medical_school:row.medical_school,
                                salary:toFloat(row.salary)
                                }});
            """
            _ = session.run(query, {})

        LOGGER.info("Loading review nodes")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Review']}' AS row
            MERGE (h:Review {{id: toInteger(row.review_id),
                                visit_id: toInteger(row.visit_id),
                                review:row.review,
                                physician_name:row.physician_name,
                                hospital_name:row.hospital_name,
                                patient_name:row.patient_name
                                }});
            """
            _ = session.run(query, {})

        LOGGER.info("Loading visit nodes")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MERGE (h:Visit {{id: toInteger(row.visit_id),
                                patient_id: toInteger(row.patient_id),
                                room_number:toInteger(row.room_number),
                                admission_type:row.admission_type,
                                test_results:row.test_results,
                                physician_id:toInteger(row.physician_id),
                                payer_id:toInteger(row.payer_id),
                                hospital_id:toInteger(row.hospital_id),
                                visit_status:row.visit_status
                                }})
            ON CREATE SET h.discharge_date=date(row.discharge_date)
            ON MATCH SET h.discharge_date=date(row.discharge_date)
            ON CREATE SET h.chief_complaint=row.chief_complaint
            ON MATCH SET h.chief_complaint=row.chief_complaint
            ON CREATE SET h.primary_diagnosis=row.primary_diagnosis
            ON MATCH SET h.primary_diagnosis=row.primary_diagnosis
            ON CREATE SET h.treatment_description=row.treatment_description
            ON MATCH SET h.treatment_description=row.treatment_description
            """
            _ = session.run(query, {})

        LOGGER.info("Loading Visit - AT -> Hospital relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MATCH (from:Visit {{id:toInteger(row.visit_id)}})
            MATCH (to:Hospital {{id:toInteger(row.hospital_id)}})
            MERGE (from)-[:AT]->(to)
            """
            _ = session.run(query, {})

        LOGGER.info("Loading Hospital - EMPLOYS -> Physician relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MATCH (from:Hospital {{id:toInteger(row.hospital_id)}})
            MATCH (to:Physician{{id:toInteger(row.physician_id)}})
            MERGE (from)-[:EMPLOYS]->(to)
            """
            _ = session.run(query, {})

        LOGGER.info("Loading Physician - TREATS -> Visit relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MATCH (from:Physician {{id:toInteger(row.physician_id)}})
            MATCH (to:Visit{{id:toInteger(row.visit_id)}})
            MERGE (from)-[:TREATS]->(to)
            """
            _ = session.run(query, {})

        LOGGER.info("Loading Patient - HAS -> Visit relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MATCH (from:Patient {{id:toInteger(row.patient_id)}})
            MATCH (to:Visit{{id:toInteger(row.visit_id)}})
            MERGE (from)-[:HAS]->(to)
            """
            _ = session.run(query, {})

        LOGGER.info("Loading Visit - WRITES -> Review relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Review']}' AS row
            MATCH (from:Visit {{id:toInteger(row.visit_id)}})
            MATCH (to:Review{{id:toInteger(row.review_id)}})
            MERGE (from)-[:WRITES]->(to)
            """
            _ = session.run(query, {})
        
        LOGGER.info("Loading Visit - COVERED_BY -> Payer relationship")
        with driver.session(database="hopitaldata") as session:
            query = f"""
            LOAD CSV WITH HEADERS
            FROM 'file:///{dict_NODES['Visit']}' AS row
            MATCH (from:Visit {{id:toInteger(row.visit_id)}})
            MATCH (to:Payer{{id:toInteger(row.payer_id)}})
            MERGE (from)-[covered_by:COVERED_BY]->(to)
            ON CREATE SET 
                covered_by.date_of_admission=date(row.date_of_admission),
                covered_by.billing_amount=toFloat(row.billing_amount)
            """
            _ = session.run(query, {})

if __name__ == "__main__":
    set_constraint()
    load_hospital_graph_from_csv()