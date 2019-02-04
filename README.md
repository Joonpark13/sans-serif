# Sans-Serif
#### Sans-Serif is the API that powers [Serif.nu](https://serif.nu).

## Setup

### Install

We recommend developing in a virtual envrionment such as [pipenv](https://pipenv.readthedocs.io/en/latest/).

Clone the repo, set up a cloud firestore databse, set up the API_URl environment variable, then run `python script.py` to populate the db.

To set up the cloud function, follow the [Cloud Functions documentation](https://firebase.google.com/docs/functions/) (the `functions` directory contains the cloud function files).

### Environment Variables

* `API_URL` The url for the Northwestern data source
* `FUNCTIONS_URL` The url for the search index creation cloud function

## Architecture

Sans-Serif is a serverless backend solution designed for use with (Serif.nu)[https://serif.nu]. It consists of a Cloud Firestore database, a Python script run on AWS Lambda for data updates, and a Cloud Function using elasticlunr for search index creation.

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

#### functions/index.js

This is the file that Cloud Functions runs when the cloud function is called.

#### functions/index.dev.js

This is a dev version of index.js meant to simulate a call to the cloud function in a local environment.

#### functions/create-index.js

This shared file contains the function that creates an elasticlunr search index for a given term's course data.

### Data Structure

