# Reckoner

This is a fun project implementing a basic forecasting platform. It is in a similar vein to the Good Judgement Project. One of the best ways to improve how good a forecaster you are is to track it! 

The project is still in development but is working as a development instance right now. As such it can be run using the Flask environment variables of 

```
set FLASK_APP="reckoner"
set FLASK_ENV="development"
```

Alternatively, if you are on Windows, there is a Powershell script provided to set these and change into a virtual environment called `venv`.

You should set up a virtual environment for this project and install the packages specified in `requirements.txt`. As such, you can install and run this project as follows:

Windows Terminal (assuming you have Python 3 as your default version)
```
git clone https://github.com/tangohead/reckoner
cd reckoner
python -m venv venv
pip3 install requirements.txt
setup_env.ps1
flask init-db
flask run
```

Bash
```
git clone https://github.com/tangohead/reckoner
cd reckoner
python3 -m venv venv
pip3 install requirements.txt
set FLASK_APP="reckoner"
set FLASK_ENV="development"
flask init-db
flask run
```

You will need to create two environment files for Docker, or set environment variables for use with `flask run`.

You will always need `db.env` of the form:
```
POSTGRES_USER='xxx'
POSTGRES_DB='xxx'
POSTGRES_PASSWORD='xxx'
```
If you are deploying, you will need `site.env` of the form:
```
POSTGRES_USER='xxx'
POSTGRES_DB='xxx'
POSTGRES_PASSWORD='xxx'
POSTGRES_HOSTNAME="db"
POSTGRES_PORT=5432
SECRET_KEY='xxx'
```
For use with `flask run`, i.e. locally, you will need to set:
```
POSTGRES_USER='xxx'
POSTGRES_DB='xxx'
POSTGRES_PASSWORD='xxx'
POSTGRES_HOSTNAME="db"
POSTGRES_PORT=5433
SECRET_KEY='xxx'
```
Note the differing Postgres port number - this helps avoid a conflict if you have a local Postgres install.

Then to run locally, do:
```
docker-compose up db -d
flask run
```
The site will be served on 5000 and will update as changes are made.

To run with `gunicorn` and Docker, just do:
```
docker-compose up
```
The site will be served on port 8000.

