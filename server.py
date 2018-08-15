import sys
from pymongo import MongoClient
from flask import Flask, jsonify

from data_getters import get_terms, get_schools



# Initializations -----------------------------------------------------------------

# Command line arguments
load_all = False
load_term = None

for i, argument in enumerate(sys.argv[1:]): # Exclude name of script
    if argument == '--load-all':
        load_all = True
    if argument == '--load-term':
        # Next argument is term id
        load_term = str(sys.argv[i])

# Initialize mongodb connection
client = MongoClient()

# Initialize flask app
app = Flask(__name__)


# DB Setup ------------------------------------------------------------------------

# If there are no term databases (First time setup)
if not any(database[:5] == 'term_' for database in client.database_names()):
    print('Running first time setup...')

    # By default, load the most recent term in the database
    if not load_all and not load_term:
        print('Loading most recent term data into database...')

        most_recent_term_id = get_terms()[0]['id']
        
        db = client['term_{0}'.format(most_recent_term_id)]
        col = db.schools
        col.insert_many(get_schools(most_recent_term_id))

        print('Loading complete.')



# Server -------------------------------------------------------------------------

def query_data(col_obj, col_lvl):
    data = []

    for item in col_obj.find({}, {'_id': False}):
        data.append(item)

    return data


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test')
def test():
    db = client.term_4720
    col = db.schools

    schools = query_data(col, 'schools')

    return jsonify(schools)

