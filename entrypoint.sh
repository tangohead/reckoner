#!/bin/bash

# check if cert exists, serve over HTTPS if so
if [ -z "$CERT_PATH" ]
then
    gunicorn -w 4 -b 0.0.0.0:4000 reckoner.wsgi:app
else
    gunicorn -w 4 -b 0.0.0.0:4000 --certfile=$CERT_PATH --keyfile=$KEY_PATH reckoner.wsgi:app
fi