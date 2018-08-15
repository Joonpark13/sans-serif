import sys
import os
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
client = MongoClient(os.environ['MONGODB_URI'])
db = client[os.environ['MONGODB_DB_NAME']]

# Initialize flask app
app = Flask(__name__)


# DB Setup ------------------------------------------------------------------------

def setup():
    # If there are no terms (First time setup)
    if len(db.collection_names()) == 0:
        print('Running first time setup...')

        # By default, load the most recent term
        if not load_all and not load_term:
            print('Loading most recent term data into database...')

            most_recent_term_id = get_terms()[0]['id']
            
            col = db['term_{0}'.format(most_recent_term_id)]
            col.insert_many(get_schools(most_recent_term_id))

            print('Loading complete.')



# Server -------------------------------------------------------------------------

def query_data(col_obj, col_lvl):
    data = []

    for item in col_obj.find({'type': col_lvl}, {'_id': False}):
        data.append(item)

    return data


@app.route('/')
def hello_world():
    return 'Hello, world!'

@app.route('/test')
def test():
    col = db.term_4720

    schools = query_data(col, 'school')

    return jsonify(schools)



if __name__ == '__main__':
    setup()

    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()

