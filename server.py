import sys
import os
from pymongo import MongoClient
from flask import Flask, jsonify



# Initializations -----------------------------------------------------------------

# Command line arguments
provided_uri = None
provided_db_name = None

for i, argument in enumerate(sys.argv[1:]): # Exclude name of script
    if argument == '--db':
        # Next argument is mongodb uri
        provided_uri = str(sys.argv[i + 2])
        # Next argument is mongodb db name
        provided_db_name = str(sys.argv[i + 3])

# Initialize mongodb connection
if provided_uri and provided_db_name:
    client = MongoBlient(provided_uri)
    db = client[provided_db_name]
else:
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client[os.environ['MONGODB_DB_NAME']]

# Initialize flask app
app = Flask(__name__)



# Server -------------------------------------------------------------------------

def query_data(collection_obj, collection_lvl):
    data = []

    for item in collection_obj.find({'type': collection_lvl}, {'_id': False}):
        data.append(item)

    return data


@app.route('/')
def hello_world():
    return 'Hello, world!'

@app.route('/search/<string:term_id>')
def search(term_id):
    collection = db.term_4720

    schools = query_data(collection, 'school')

    return jsonify(schools)



if __name__ == '__main__':
    app.run()

