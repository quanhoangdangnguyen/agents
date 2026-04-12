# Imagine these come from a CSV load
drug_ids = ["DB001", "DB002", "DB003"]
drug_names = ["Aspirin", "Paracetamol", "Ibuprofen"]

# Create the lookup map
drug_lookup = list(zip(drug_ids, drug_names))
print(drug_lookup)