from neo4j import GraphDatabase

# Connection details
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "123456789")

from pathlib import Path

def check_connection():
    try:
        # The 'with' statement handles closing the driver automatically
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("Connection Successful!")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check_connection()
    # Create a path object
    p = Path(r"D:\Studying\AI agent\extra\LLM RAG Chatbot with LangChain and Neo4j\data\hospitals.csv")

    # Convert to URI
    file_url = p.as_uri()

    print(file_url)
    # Output: file:///D:/Studying/AI%20agent/extra/data/hospitals.csv