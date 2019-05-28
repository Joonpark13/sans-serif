import sys
import os
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from data_getters import get_terms, get_schools, get_subjects, get_courses, get_sections


FUNCTIONS_URL = os.environ['FUNCTIONS_URL']


def parse_command_line_arguments(args):
    options = {
        'name': None,
        'value': None,
        'env': 'dev'
    }

    for i, argument in enumerate(args[1:]): # Exclude name of script
        if argument == '--production':
            options['env'] = 'prod'


    for i, argument in enumerate(args[1:]): # Exclude name of script
        if argument == '--initialize':
            options['name'] = 'initialize'
        elif argument == '--check-for-new-term':
            options['name'] = 'check-for-new-term'
        elif argument == '--load-term-data':
            options['name'] = 'load-term-data'
            # Next argument is term id
            options['value'] = str(args[i + 2])
        elif argument == '--update-term-data':
            options['name'] = 'update-term-data'
            try:
                next_arg = args[i + 2]
                if not next_arg[:2] == '--':
                    options['value'] = str(next_arg)
            except IndexError: 
                # Next argument doesn't exist - go with default behavior
                pass

    return options


def get_newest_term_id(terms):
    return max([term['id'] for term in terms])


def batch_write(db, collection, data, doc_key = None):
    counter = 0
    BATCH_LIMIT = 500

    batch = db.batch()
    for data_obj in data:
        if counter == BATCH_LIMIT:
            batch.commit()
            batch = db.batch()
            counter = 0

        if doc_key:
            new_doc = collection.document(data_obj[doc_key])
        else:
            new_doc = collection.document()
        batch.set(new_doc, data_obj)
        counter += 1

    batch.commit()


def db_has_term(db, term_id):
    schools_docs = db.collection('terms').document(term_id).collection('schools').get()
    for _ in schools_docs:
        return True
    return False


def get_most_recent_term_in_db(db):
    terms = db.collection('terms').get()
    return max(terms, key=lambda term: term.id).to_dict()


def load_term(db, term_id, delete_first = False):
    print('Loading term {0} data...'.format(term_id))

    terms_data = get_terms()
    term = list(filter(
        lambda term_obj: term_obj['id'] == term_id,
        terms_data
    ))[0]

    schools_data = get_schools(term_id)

    print('Schools data fetched.')

    subjects_data = []
    for school in schools_data:
        subjects_data = subjects_data + get_subjects(term_id, school['id'])

    print('Subjects data fetched.')

    courses_data = []
    for subject in subjects_data:
        courses_data = courses_data + get_courses(
            term_id,
            subject['schoolId'],
            subject['id']
        )

    print('Courses data fetched.')

    sections_data = []
    for course in courses_data:
        sections_data = sections_data + get_sections(
            term_id,
            course['schoolId'],
            course['subjectId'],
            course['id']
        )

    print('Sections data fetched.')

    if delete_first and db_has_term(db, term_id):
        print('Deleting previous data...')
        terms_doc = db.collection('terms').document(term_id)
        delete_subcollection(db, terms_doc, 'schools')
        delete_subcollection(db, terms_doc, 'subjects')
        delete_subcollection(db, terms_doc, 'courses')
        delete_subcollection(db, terms_doc, 'sections')
        db.collection('terms').document(term_id).delete()

    db.collection('terms').document(term['id']).set(term)
    current_term_doc = db.collection('terms').document(term_id)
    batch_write(db, current_term_doc.collection('schools'), schools_data)
    batch_write(db, current_term_doc.collection('subjects'), subjects_data)
    batch_write(db, current_term_doc.collection('courses'), courses_data)
    batch_write(db, current_term_doc.collection('sections'), sections_data)

    print('Data written to database.')

    requests.post(FUNCTIONS_URL, params={ 'termId': term_id })

    print('Search index created.')

    print('Data loading complete.')


def delete_subcollection(db, doc, subcollection_name):
    counter = 0
    BATCH_LIMIT = 500

    batch = db.batch()
    for data_doc in doc.collection(subcollection_name).get():
        if counter == BATCH_LIMIT:
            batch.commit()
            batch = db.batch()
            counter = 0

        batch.delete(data_doc.reference)
        counter += 1
    batch.commit()



if __name__ == "__main__":
    options = parse_command_line_arguments(sys.argv)

    dev_creds = './sans-serif-northwestern-728315dd9469.json'
    prod_creds = './sans-serif-prod-firebase-adminsdk-osgyv-36e8af3b7e.json'
    if options['env'] == 'prod':
        cred = credentials.Certificate(prod_creds)
        print('USING PRODUCTION DATABASE!')
    else:
        cred = credentials.Certificate(dev_creds)

    firebase_admin.initialize_app(cred)

    db = firestore.client()

    if options['name'] == None:
        print('''
        No valid option was specified. Did you mean one of the following options?
            --initialize
            --check-for-new-term
            --load-term-data
            --update-term-data
        ''')

    else:
        if options['name'] == 'initialize':
            newest_term_id = get_newest_term_id(get_terms())
            load_term(db, newest_term_id)

        if options['name'] == 'check-for-new-term':
            newest_term_id = get_newest_term_id(get_terms())
            if str(newest_term_id) == str(get_most_recent_term_in_db(db)['id']):
                print('No new term found.')
            else:
                print('New term found: {0}'.format(newest_term_id))

        elif options['name'] == 'load-term-data':
            term_id = options['value']
            if db_has_term(db, term_id):
                print('Term {0} already loaded.'.format(term_id))
            else:
                load_term(db, term_id)

        elif options['name'] == 'update-term-data':
            if options['value']:
                term_to_update = options['value']
            else:
                term_to_update = get_most_recent_term_in_db(db)['id']

            load_term(db, term_to_update, True)

