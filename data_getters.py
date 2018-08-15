import os
import json
from html.parser import HTMLParser
import requests



# Helper functions

parser = HTMLParser()


def make_request(query, level):
    # Possible levels:
    # terms
    # schools
    # subjects
    # courses
    # sections

    # Prepare query with correct ending
    if level == 'terms':
        query = 'index-v2.json'
    elif level == 'details':
        query += '-v2.json'
    else:
        query += '/index-v2.json'

    r = None
    error_counter = 0
    while r is None:
        if error_counter > 5:
            print("Too many connection errors occured.")
            quit()
        try:
            r = requests.get(os.environ['API_URL'] + query)
            error_counter = 0
        except requests.exceptions.ConnectionError:
            error_counter += 1

    # If API has no real data to return, it will return the following:
    # [,{"ignore":"<xml></xml> "}]
    # which is not parseable json due to the comma.
    if r.text[1] == ',':
        return []
    try:
        body = r.json()
    except json.decoder.JSONDecodeError:
        # Some data contains a few problematic characters, such as a \' or a tab
        # which disrupts the json parsing. Replace with appropriate substitutes,
        # then re-attempt json parsing.
        parsedStringText = r.text.replace('\\%', '%').replace('\\\'', '\'').replace('\t', ' ')
        try:
            body = json.loads(parsedStringText)
        except json.decoder.JSONDecodeError:
            return []
            # Known error cases:
            # parsedStringText being '<xml/> "}]'
            # parsedStringText having quotes inside of values (&quot; before converting to string)
    # Parse out last non-data term
    # Object looks like this: {'ignore': '<xml></xml> '}
    try:
        body.remove({'ignore': '<xml></xml> '})
    except ValueError:
        pass # In rare cases where this object is not in the data, we do not need to remove anything.

    return body


def get_details(term, school, subject, course, section):
    # term is the term id
    # school is the school id
    # subject is the subject abbv
    # course is the course abbv
    # section is the section id
    query = term + '/' + school + '/' + subject + '/' + course + '/' + section
    data = make_request(query, 'details')
    if data:
        for detail in data:
            for desc in detail['descriptions']:
                desc['value'] = parser.unescape(desc['value'])
    return data



# Data getters

def get_terms():
    return make_request('', 'terms')


def get_schools(term):
    # term is the term id
    data =  make_request(term, 'schools')
    for school in data:
        school['term'] = term
    return data


def get_subjects(term, school):
    # term is the term id
    # school is the school id
    data = make_request(term + '/' + school, 'subjects')
    for subject in data:
        subject['term'] = term
        subject['school'] = school
        del subject['path']
    return data


def get_courses(term, school, subject):
    # term is the term id
    # school is the school id
    # subject is the subject abbv
    data = make_request(term + '/' + school + '/' + subject, 'courses')
    if data:
        for course in data:
            course['term'] = term
            course['school'] = school
            course['subject'] = subject
            course['name'] = parser.unescape(course['name'])
            del course['path']
    return data


def get_sections(term, school, subject, course):
    # term is the term id
    # school is the school id
    # subject is the subject abbv
    # course is the course abbv
    query = term + '/' + school + '/' + subject + '/' + course
    data = make_request(query, 'sections')
    parsed = []
    if data:
        for section in data:
            section['term'] = term
            section['school'] = school
            section['subject'] = subject
            section['course'] = course
            section['name'] = parser.unescape(section['name'])
            section['overview_of_class'] = parser.unescape(section['overview_of_class'])
            section['topic'] = parser.unescape(section['topic'])
            try:
                detail = get_details(term, school, subject, course, section['id'])[0]
            except IndexError:
                # Don't include section at all if details json is not valid
                continue
            del detail['name'] # 'name' field of details is the same as section id
            del detail['topic'] # redundant field
            try:
                del detail['instructors'] # redundant field
            except KeyError:
                pass
            del section['meeting_time'] # redundant field
            del section['path'] # redundant field
            section.update(detail)
            parsed.append(section)
    return parsed

