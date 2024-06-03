
# Define a function to insert records only if the key does not exist
def insert_if_not_exists(collection, records, filter):
    inserted_count = 0
    records = records[:filter]
    
    last_update = records[0]['key']
    
    for record in records:
        # Create key
        
        key = 'key'
        
        # Check if the key exists in the collection
        filter = {key: record[key]}
        if not collection.find_one(filter):
            # Insert the record if the key does not exist
            collection.insert_one(record)
            inserted_count += 1
            
    print(f"{last_update} - {inserted_count/len(records)}")
    #return inserted_count
