from citrination_client import CitrinationClient
from os import environ

client = CitrinationClient(environ['CITRINATION_API_KEY'], 'https://citrination.com')
response = client.create_data_set("Weymouth - Test dataset", "A scrap dataset for testing - Terry E Weymouth")
print(response)
