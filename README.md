# Sans-Serif
#### Sans-Serif is the API that powers [Serif.nu](https://serif.nu).

## Setup

### Install

We recommend developing in a virtual envrionment such as [pipenv](https://pipenv.readthedocs.io/en/latest/).

Clone the repo, set up a cloud firestore databse, set up the API_URl environment variable, then run `python script.py` to populate the db.

### Environment Variables

* `API_URL` The url for the Northwestern data source

## Architecture

### The Sans-Serif Server

Sans-Serif is a cloud firestore service that consists of endpoints designed to serve [Serif.nu](https://serif.nu).

### Heroku Scheduler

Heroku's scheduler allows us to automate data updates during registration season when demand is high and speed is important. A typical registration season may look like this:

On the day when course data for the next quarter is predicted to be released, we schedule `python script.py --check-for-new-term` to be run early every morning until the new term data is made available and is loaded into our database. Then, when pre-registration begins, we schedule `python script.py --update` early every morning to keep the data up to date, until registration week ends. Afterwards, the data is updated manually at the maintainer's discretion.

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

### Data Structure

