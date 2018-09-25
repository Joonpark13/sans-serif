import sys
import os
from pymongo import MongoClient

from data_getters import get_terms, get_schools, get_subjects, get_courses, get_sections
from helpers import get_collection



def check_if_term_exists(db, term_id):
    collections = db.list_collection_names()
    for col_name in collections:
        if term_id == col_name[5:]: # term names are in the format of term_4710
            return True
    return False


def get_most_recent_term():
   return get_terms()[0]['id']


def handle_command_line_arguments(args):
    options = {
        'option_name': None,
        'option_value': None,
        'db_uri': None,
        'db_name': None,
    }

    for i, argument in enumerate(args[1:]): # Exclude name of script
        if argument == '--db':
            # Next argument is mongodb uri
            options['db_uri'] = str(args[i + 2])
            # Next argument is mongodb db name
            options['db_name'] = str(args[i + 3])
        elif argument == '--load-term':
            options['option_name'] = 'load-term'
            # Next argument is term id
            options['option_value'] = str(args[i + 2])
        elif argument == '--update':
            options['option_name'] = 'update'
            try:
                next_arg = args[i + 2]
                if not next_arg[:2] == '--':
                    options['option_value'] = str(next_arg)
            except IndexError: 
                # Next argument doesn't exist - go with default behavior
                pass

    return options


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
    print('Loading term {0} data into database...'.format(term_to_load))
    load_term_data(collection, term_to_load)
    print('Loading complete.')


def create_search_index(collection):
    collection.create_index([('subject', 'text'), ('abbv', 'text'), ('name', 'text')])



if __name__ == "__main__":
    options = handle_command_line_arguments(sys.argv)

    # Initialize mongodb connection
    if options['db_uri'] and options['db_name']:
        print('Custom database specified.')
        client = MongoClient(options['db_uri'])
        db = client[options['db_name']]
    else:
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client[os.environ['MONGODB_DB_NAME']]

    # By default, load the most recent term
    if not options['option_name']:
        most_recent_term_id = get_most_recent_term()
        if check_if_term_exists(db, most_recent_term_id):
            print('Most recent term already loaded.')
        else:
            collection = get_collection(db, most_recent_term_id)
            print('Loading most recent term by default.')
            load_data(collection, most_recent_term_id)
            create_search_index(collection)

    elif options['option_name'] == 'load-term':
        if check_if_term_exists(db, options['option_value']):
            print('Term {0} already loaded.'.format(options['option_value']))
        else:
            collection = get_collection(db, options['option_value'])
            load_data(collection, options['option_value'])
            create_search_index(collection)

    elif options['option_name'] == 'update':
        if options['option_value']:
            term_to_update = options['option_value']
        else:
            term_to_update = get_most_recent_term()

        if not check_if_term_exists(db, term_to_update):
            print('Term data does not exist.')
        else:
            # Erase existing data first
            collection = get_collection(db, term_to_update)
            print('Purging existing data')
            collection.drop()

            load_data(collection, term_to_update)
            create_search_index(collection)

