from dotenv import load_dotenv
load_dotenv(override=True)

# from src.chains.hospital_review_chain import reviews_vector_chain
# from src.chains.hospital_cypher_chain import hospital_cypher_chain

# query = """
#         What have patients said about hospital efficiency?
#         Mention details from specific reviews.
#         """

# response = reviews_vector_chain.invoke(query)

# print(response.get("result"))

# question = """What is the average visit duration for emergency visits in North Carolina?"""
# question="""What is the average salary of physician?"""
# response = hospital_cypher_chain.invoke(question)

# print(response)

from src.tools.wait_times import get_current_wait_times,get_most_available_hospital

print(get_current_wait_times("Wallace-Hamilton"))

print(get_current_wait_times("fake hospital"))

print(get_most_available_hospital(None))

