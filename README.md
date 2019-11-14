# Sans-Serif
#### Sans-Serif is the data collection script that powers [Serif.nu](https://serif.nu).

## Setup

We recommend developing in a virtual envrionment such as [pipenv](https://pipenv.readthedocs.io/en/latest/).

### Environment Variables

* `API_URL` The url for the Northwestern data source

## Reference

### Files

#### data_getters.py

Contains the helper functions that query the data from the Northwestern data source.

#### update.py

Usage: `python update.py 4770`

`4770` is the term id - replace this with the id of the term that you want to grab the data for. Running this will create a `data/4770` directory, within which will contain the json files for that term. If this directory already exists, all of the existing json in it will be removed and re-fetched. the `data` directory will also have a special `terms.json` file which will be updated with a new term if you run this script for the first time for a given term. See the Serif.nu data update documentation on how to transfer these json files over to Serif.nu correctly.

Keep in mind that these scripts can run for a very long time.

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
  schedules: array of schedule objects,
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
