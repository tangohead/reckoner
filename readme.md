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

You will need to create `credentials.py` in the `reckoner` directory. Currently, this should contain the following:
```
SECRET_KEY='your_flask_secret_key_here'
```

This will be updated when the project is ready to be run in deployment.

