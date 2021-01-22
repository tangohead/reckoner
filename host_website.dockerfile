FROM python:3.8

WORKDIR /site/
COPY ./reckoner /site/reckoner/

COPY requirements.txt .

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY entrypoint.sh .
RUN chmod u+x entrypoint.sh

RUN ls

ENTRYPOINT [ "./entrypoint.sh" ]
