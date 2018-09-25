# Sans-Serif
#### Sans-Serif is the API that powers [Serif.nu](https://serif.nu).

## Setup

### Install

We recommend developing in a virtual envrionment such as [pipenv](https://pipenv.readthedocs.io/en/latest/).

Clone the repo, set up a local MongoDB, set up the environment variables, then run `python script.py` to populate the db. Run `python server.py` to start the server.

### Environment Variables

The required envrionment variables are as follows:

* `API_URL` The url for the Northwestern data source
* `FLASK_APP` This should be `server.py`, in case you want to run the server through the `flask run` command.
* `MONGODB_URI`
* `MONGODB_DB_NAME`
* `CORS_ALLOWED` The allowed url for the front end (likely your local development url for Serif.nu).

## Architecture

### The Sans-Serif Server

Sans-Serif is a Flask back-end application that consists of endpoints designed to serve [Serif.nu](https://serif.nu). The server serves data from a [MongoDB](https://www.mongodb.com/) database.

### Heroku Scheduler

Heroku's scheduler allows us to automate data updates during registration season when demand is high and speed is important. A typical registration season may look like this:

On the day when course data for the next quarter is predicted to be released, we schedule `python script.py` to be run early every morning until the new term data is made available and is loaded into our database. Then, when pre-registration begins, we schedule `python script.py --update` early every morning to keep the data up to date, until registration week ends. Afterwards, the data is updated manually at the maintainer's discretion.

## API Reference

### Files

#### data_getters.py
Contains the helper functions that query the data from the Northwestern data source.

#### script.py
This is the script file that is used to upload and update the course data into the MongoDB.

By default, this script will load the most recent term data into the MongoDB when run. This is useful when initializing the database for the first time. This will not overwrite existing data if the most recent term data is already loaded into the database.

Other usage is as follows (*be aware that with the exception of `--db`, the following command line arguments are not intended to be used at the same time with one another. Each command line argument is encapsulated for a clear and distinct purpose.*):

`--db` allows you to specify the MongoDB by providing the URI and database name. You must specify both. This is the only command line argument that can be combined with other arguments. Example:

```
python script.py --db {MY_MONGO_DB_URI} {MY_MONGO_DB_NAME}
```

`--load-term` allows you to specify the term id for the term that you want loaded into the database. This will not overwrite existing data if this term data already exists in the database. Example:

```
python script.py --load-term 4710
```

`--update` allows you to update the most recent or specified term. This command **will** overwrite existing data. To update the most recent term:

```
python script.py --update
```

Or to update a specific term:

```
python script.py --update 4710
```

#### server.py
Flask server, serves data from the MongoDB. Endpoints listed below.

### Endpoints
