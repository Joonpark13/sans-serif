import sys
import os
from pymongo import MongoClient

from data_getters import get_terms, get_schools, get_subjects, get_courses, get_sections
from helpers import get_collection

def load_term_data(collection, term_id):
    schools_data = get_schools(term_id)

    subjects_data = []
    for school in schools_data:
        subjects_data = subjects_data + get_subjects(term_id, school['id'])

    courses_data = []
    for subject in subjects_data:
        courses_data = courses_data + get_courses(term_id, subject['school'], subject['abbv'])

    sections_data = []
    for course in courses_data:
        sections_data = sections_data + get_sections(term_id, course['school'], course['subject'], course['abbv'])

    collection.insert_many(schools_data)
    collection.insert_many(subjects_data)
    collection.insert_many(courses_data)
    collection.insert_many(sections_data)


def load_data(collection, term_to_load):
    # If collection doesn't exist
    if collection.count_documents({}) == 0:
        print('Loading term {0} data into database...'.format(term_to_load))
        load_term_data(collection, term_to_load)
        print('Loading complete.')
    else:
        print('Term already loaded.')


def create_search_index(collection):
    collection.create_index([('subject', 'text'), ('abbv', 'text'), ('name', 'text')])



if __name__ == "__main__":
    # Command line arguments
    term_to_load = None
    provided_uri = None
    provided_db_name = None

    for i, argument in enumerate(sys.argv[1:]): # Exclude name of script
        if argument == '--load-term':
            # Next argument is term id
            term_to_load = str(sys.argv[i + 2])
        elif argument == '--db':
            # Next argument is mongodb uri
            provided_uri = str(sys.argv[i + 2])
            # Next argument is mongodb db name
            provided_db_name = str(sys.argv[i + 3])

    # Initialize mongodb connection
    if provided_uri and provided_db_name:
        client = MongoClient(provided_uri)
        db = client[provided_db_name]
    else:
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client[os.environ['MONGODB_DB_NAME']]

    # By default, load the most recent term
    if not term_to_load:
        most_recent_term_id = get_terms()[0]['id']
        collection = get_collection(db, most_recent_term_id)
        print('Loading most recent term by default')
        load_data(collection, most_recent_term_id)
        create_search_index(collection)
    else:
        collection = get_collection(db, term_to_load)
        load_data(collection, term_to_load)
        create_search_index(collection)

