import sys
import shutil
import os
import json
from data_getters import get_terms, get_schools, get_subjects, get_courses, get_sections

TERM_DIR_TEMPLATE = './data/{0}'

def fetch_data(term_id):
    print('Fetching term {0} data...'.format(term_id))

    terms_data = get_terms()
    term_data = list(filter(
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

    return {
        'term': term_data,
        'schools': schools_data,
        'subjects': subjects_data,
        'courses': courses_data,
        'sections': sections_data
    }

def delete_term(term_id):
    print('Removing old files...')
    shutil.rmtree(TERM_DIR_TEMPLATE.format(term_id))

    with open('data/terms.json') as terms_file:
        terms_data = json.load(terms_file)
        filtered_data = []
        for term in terms_data:
            if term['id'] != term_id:
                filtered_data.append(term)

    with open('data/terms.json', 'w') as terms_file:
        json.dump(filtered_data, terms_file)

def create_files(data, term_id):
    print('Writing files...')
    term_dir = TERM_DIR_TEMPLATE.format(term_id)
    os.mkdir(term_dir)

    with open('data/terms.json') as terms_file:
        terms_data = json.load(terms_file)
        terms_data.append(data['term'])

    with open('data/terms.json', 'w') as terms_file:
        json.dump(terms_data, terms_file)

    with open('{0}/schools.json'.format(term_dir), 'w') as schools_file:
        json.dump(data['schools'], schools_file)

    with open('{0}/subjects.json'.format(term_dir), 'w') as subjects_file:
        json.dump(data['subjects'], subjects_file)

    with open('{0}/courses.json'.format(term_dir), 'w') as courses_file:
        json.dump(data['courses'], courses_file)

    with open('{0}/sections.json'.format(term_dir), 'w') as sections_file:
        json.dump(data['sections'], sections_file)

    print('Files created.')

if __name__ == "__main__":
    term_id = sys.argv[1]

    data = fetch_data(term_id)

    if os.path.exists(TERM_DIR_TEMPLATE.format(term_id)):
        delete_term(term_id)

    create_files(data, term_id)

