# Dockerfile for Origin Flask E2E Test Site

FROM ubuntu

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python-dev python-pip
RUN pip install pip --upgrade

ADD flasksite /opt/flasksite

RUN pip install -r /opt/flasksite/requirements.txt

EXPOSE 80

CMD python /opt/flasksite/test_app.py
