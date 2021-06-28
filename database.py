from tinymongo import TinyMongoClient

#Connect to database
connection = TinyMongoClient("mercari")
db = connection.mercari

#Get input from user
type_ = input("delete or add?\n")
if type_ == "delete":
    queries = db.queries.find()
    if queries.count != 0:
        for query in queries:
            print(f"[{query['_id']}] - [{query['search_query']}]")
        query_id = input("Which query would you like to delete?\n")
        db.queries.remove({'_id':query_id})
    else:
        print("The database is empty")

elif type_ == "add":
    search_query = input("Enter the search query:\n").strip()
    desired_price = float(input("Enter the desired price of the item:\n"))

    #Add to database
    db.queries.insert_one({"search_query": search_query, "desired_price": desired_price})