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
    # details

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
        # Some data contains a few problematic characters, such as a \'
        # or a tab which disrupts the json parsing. Replace with
        # appropriate substitutes, then re-attempt json parsing.
        parsedStringText = r.text.replace('\\%', '%').replace('\\\'', '\'').replace('\t', ' ')
        try:
            body = json.loads(parsedStringText)
        except json.decoder.JSONDecodeError:
            return []
            # Known error cases:
            # parsedStringText being '<xml/> "}]'
            # parsedStringText having quotes inside of values (&quot;
            # before converting to string)
    # Parse out last non-data term
    # Object looks like this: {'ignore': '<xml></xml> '}
    try:
        body.remove({'ignore': '<xml></xml> '})
    except ValueError:
        # In rare cases where this object is not in the data, we do not
        # need to remove anything.
        pass

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


def format_time(time_str):
    # Format: 1:50PM
    hour = int(time_str.split(':')[0])
    minute = int(time_str.split(':')[1][:2])
    ampm = time_str[-2:]

    if (ampm == 'AM'):
        if hour == 12:
            formatted_hour = 0
        else:
            formatted_hour = hour
    else:
        if hour == 12:
            formatted_hour = hour
        else:
            formatted_hour = hour + 12

    return {
        'hour': formatted_hour,
        'minute': minute
    }


def format_meeting_time(meeting_time, meeting_location):
    # Format: MoWeFr 12:00PM - 1:50PM
    split_meeting_time = meeting_time.split()

    if (len(split_meeting_time) == 4):
        dow_str = meeting_time.split()[0]
        hour_str = meeting_time.split()[1]
        minute_str = meeting_time.split()[3]
        return {
            'dow': [dow_str[i:i+2] for i in range(0, len(dow_str), 2)],
            'start': format_time(hour_str),
            'end': format_time(minute_str),
            'location': meeting_location
        }

    return {
        'dow': 'TBA',
        'start': 'TBA',
        'end': 'TBA',
        'location': meeting_location
    }


def format_schedule(meeting_info):
    formatted = []
    for meeting_obj in meeting_info:
        formatted.append(
            format_meeting_time(
                meeting_obj['meet_t'],
                meeting_obj['meet_l']
            )
        )
    
    return formatted


def format_associated_classes(associated_classes):
    return list(map(lambda associated_class: {
        'type': associated_class['component'],
        'schedule': format_meeting_time(
            associated_class['meeting_time'],
            associated_class['room']
        )
    }, associated_classes))



# Data getters

def get_terms():
    data = make_request('', 'terms')

    return list(map(lambda term: {
        'id': term['id'],
        'name': term['term']
    }, data))


def get_schools(term_id):
    data =  make_request(term_id, 'schools')

    return list(map(lambda school: {
        'id': school['id'],
        'termId': term_id,
        'name': school['name']
    }, data))


def get_subjects(term_id, school_id):
    data = make_request(
        '{0}/{1}'.format(term_id, school_id),
        'subjects'
    )

    return list(map(lambda subject: {
        'id': subject['abbv'],
        'termId': term_id,
        'schoolId': school_id,
        'name': subject['name']
    }, data))


def get_courses(term_id, school_id, subject_id):
    data = make_request(
        '{0}/{1}/{2}'.format(term_id, school_id, subject_id),
        'courses'
    )
    
    return list(map(lambda course: {
        'id': course['abbv'],
        'termId': term_id,
        'schoolId': school_id,
        'subjectId': subject_id,
        'name': course['name']
    }, data))


def get_sections(term_id, school_id, subject_id, course_id):
    def format_sections_and_details(section):
        result = {
            'id': section['id'],
            'termId': term_id,
            'schoolId': school_id,
            'subjectId': subject_id,
            'courseId': course_id,
            'name': section['name'],
            'sectionNumber': section['section'],
            'instructors': section['instructor']
        }

        try:
            detail = get_details(
                term_id,
                school_id,
                subject_id,
                course_id,
                section['id']
            )[0]
        except IndexError:
            # Don't include section at all if details json is not valid
            return

        result['topic'] = detail['topic']
        result['schedules'] = format_schedule(detail['class_mtg_info'])
        result['descriptions'] = detail['descriptions']
        if 'associated_classes' in detail:
            result['associatedClasses'] = format_associated_classes(detail['associated_classes'])

        return result

    data = make_request(
        '{0}/{1}/{2}/{3}'.format(
            term_id,
            school_id,
            subject_id,
            course_id
        ),
        'sections'
    )

    return list(map(format_sections_and_details, data))
