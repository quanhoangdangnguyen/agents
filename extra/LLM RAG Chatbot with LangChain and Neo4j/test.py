from dotenv import load_dotenv
load_dotenv(override=True)

from src.chains.hospital_review_chain import reviews_vector_chain



query = """
        What have patients said about hospital efficiency?
        Mention details from specific reviews.
        """

response = reviews_vector_chain.invoke(query)

response.get("result")
