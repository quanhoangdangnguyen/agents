from dotenv import load_dotenv
import os

load_dotenv(override=True)

for key, value in os.environ.items():
    print(f"{key}: {value}")