import sys
import os
from pymongo import MongoClient
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from bson.objectid import ObjectId

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
CORS(app, origins=[os.environ['CORS_ALLOWED'], os.environ['CORS_ALLOWED_LOCAL']])



# Helpers ------------------------------------------------------------------------

def stringify_ids(search_result):
    '''
    Takes a document or a list of PyMongo documents and converts their _ids to strings

    '''

    def stringify_single_document_id(doc):
        doc['_id'] = str(doc['_id'])
        return doc

    if isinstance(search_result, list):
        stringified_results = []
        for result in search_result:
            stringified_results.append(stringify_single_document_id(result))
        return stringified_results

    else:
        return stringify_single_document_id(search_result)


def cursor_to_list(results_cursor):
    results_list = []
    for result in results_cursor:
        results_list.append(result)

    return results_list



# Server -------------------------------------------------------------------------

@app.route('/')
def index():
    return redirect('https://github.com/Joonpark13/sans-serif')


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
    }).sort([('score', { '$meta': 'textScore' })])

    search_results = cursor_to_list(cursor)

    return jsonify(stringify_ids(search_results))


@app.route('/schools')
def schools():
    term_id = request.args.get('term_id')

    collection = get_collection(db, term_id)
    cursor = collection.find({
        'type': 'school'
    })

    search_results = cursor_to_list(cursor)

    return jsonify(stringify_ids(search_results))


@app.route('/sections')
def sections():
    term_id = request.args.get('term_id')
    school_abbv = request.args.get('school_abbv')
    subject_abbv = request.args.get('subject_abbv')
    course_abbv = request.args.get('course_abbv')

    collection = get_collection(db, term_id)
    cursor = collection.find({
        'type': 'section',
        'school': school_abbv,
        'subject': subject_abbv,
        'course': course_abbv
    })

    search_results = cursor_to_list(cursor)

    return jsonify(stringify_ids(search_results))



if __name__ == '__main__':
    app.run()

