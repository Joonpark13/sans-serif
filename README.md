# Sans-Serif
#### Sans-Serif is the API that powers [Serif.nu](https://serif.nu).

## Setup

### Install

We recommend developing in a virtual envrionment such as [pipenv](https://pipenv.readthedocs.io/en/latest/).

Clone the repo. To use the Python scripts for fetching the data and uploading it to Cloud Firestore, you'll need the `API_URL` environment variable and your own Cloud Firestore. (See "Environment Variables" below)

To set up the cloud function, which is required for the search index creation, follow the [Cloud Functions documentation](https://firebase.google.com/docs/functions/) (the `functions` directory contains the cloud function files).

### Environment Variables

* `API_URL` The url for the Northwestern data source
* `FUNCTIONS_URL` The url for the search index creation cloud function
* You will also need a Firebase admin json file in the root directory. See the [Python Cloud Firestore docs](https://firebase.google.com/docs/firestore/quickstart) to learn how to set up a service account and download the necessary json file. Specifying the `--production` flag to any of the scripts will require having a separate json for the prod firebase.

## Architecture

Sans-Serif is a serverless backend solution designed for use with [Serif.nu](https://serif.nu). It consists of a Cloud Firestore database, a Python script run on AWS Lambda for data updates, and a Cloud Function using elasticlunr for search index creation.

## Reference

### Files

#### data_getters.py

Contains the helper functions that query the data from the Northwestern data source.

#### script.py

This is the script file that is used to upload and update the course data into cloud firestore.

*Be aware that the command line arguments are not intended to be used at the same time with one another. Each command line argument is encapsulated for a clear and distinct purpose.*

`--initialize` loads the data for the most recent term into the database. Example:

```
python script.py --initialize
```

`--check-for-new-term` checks the API to see if data for a new term has been published. Example:

```
python script.py --check-for-new-term
```

`--load-term-data` allows you to specify the term id for the term that you want loaded into the database. This will not overwrite existing data if this term data already exists in the database. Example:

```
python script.py --load-term-data 4710
```

Keep in mind that loading term data can take a very long time.

`--update-term-data` allows you to update the most recent term stored in the database or a specified term. This command **will** overwrite existing data. To update the most recent term in the database:

```
python script.py --update-term-data
```

Or to update a specific term:

```
python script.py --update-term-data 4710
```

Keep in mind that updating term data can take a very long time.

To run these scripts using the production database, specify the `--production` flag in addition to any of the scripts.

#### functions/index.js

This is the file that Cloud Functions runs when the cloud function is called.

#### functions/index.dev.js

This is a dev version of index.js meant to simulate a call to the cloud function in a local environment.

#### functions/create-index.js

This shared file contains the function that creates an elasticlunr search index for a given term's course data.

### Data Structure

The data in Cloud Firestore is structured as follows:

- At the root level, there is a `terms` collection.
- This `terms` collection contains term documents.
- A term document consists of the `schools`, `subjects`, `courses`, and `sections` subcollections, along with its own fields (described below).

#### Term

A "term" is equivalent to a quarter, such as 'Winter 2019' or 'Summer 2014'.

```
{
  id: string,
  name: string,
  searchIndex: string (stringified JSON that represents an elasticlunr search index)
}
```

#### School

A "school" is equivalent to a college within Northwestern, such as 'Weinberg' or 'McCormick'.

```
{
  id: string,
  termId: string (equal to the id of the term to which this school belongs),
  name: string
}
```

#### Subject

A "subject" is equivalent to a department within a college, such as 'EECS' or 'PHYSICS'.

```
{
  id: string,
  termId: string (equal to the id of the term to which this subject belongs),
  schoolId: string (equal to the id of the school to which this subject belongs),
  name: string
}
```

#### Course

A "course" is equivalent to a class offering, such as 'EECS 101-0' or 'PHYSICS 135-3'.

```
{
  id: string,
  termId: string (equal to the id of the term to which this course belongs),
  schoolId: string (equal to the id of the school to which this course belongs),
  subjectId: string (equal to the id of the subject to which this course belongs),
  name: string
}
```

#### Section

A "section" is equivalent to a specific section of a class, such as 'EECS 111-0 Section 20'.

```
{
  id: string,
  termId: string (equal to the id of the term to which this section belongs),
  schoolId: string (equal to the id of the school to which this section belongs),
  subjectId: string (equal to the id of the subject to which this section belongs),
  courseId: string (equal to the id of the course to which this section belongs),
  name: string,
  sectionNumber: string,
  topic: string,
  descriptions: array of description objects,
  instructors: array of strings (where each string is an instructor name),
  schedule: array of schedule objects,
  * associatedClasses: array of associated class objects
}
```
`*` may not exist

Description object:

```
{
  name: string,
  value: string
}
```

Schedule object:

```
{
  dow: array of strings (each string will be one of 'Mo', 'Tu', 'We', 'Th', or 'Fr'),
  start: {
    hour: int (0 to 23),
    minute: int (0 to 59)
  },
  end: {
    hour: int (0 to 23),
    minute: int (0 to 59)
  }
  location: string
}
```

So, if you wanted to grab all PHYSICS courses in Winter 2019, you would get the `courses` subcollection from the term object with the `termId` of `'4730'`, then get all documents from that subcollection that match the `schoolId` of `'WCAS'` and `subjectId` of `'PHYSICS'`.

Associated class object:

```
{
  type: string,
  schedule: schedule object
}
```
