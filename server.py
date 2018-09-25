import sys
import os
from pymongo import MongoClient
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

from helpers import get_collection



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
CORS(app, origins=[os.environ['CORS_ALLOWED']])



# Server -------------------------------------------------------------------------

@app.route('/')
def index():
    return redirct('https://github.com/Joonpark13/sans-serif')

@app.route('/search')
def search():
    term_id = request.args.get('term_id')
    search_query = request.args.get('search_query')

    collection = get_collection(db, term_id)
    cursor = collection.find({
        'type': 'course',
        '$text': { '$search': search_query }
    }, {
        'score': { '$meta': 'textScore' },
        '_id': False
    }).sort([('score', { '$meta': 'textScore' })])

    search_results = []
    for search_result in cursor:
        search_results.append(search_result)

    return jsonify(search_results)



if __name__ == '__main__':
    app.run()

