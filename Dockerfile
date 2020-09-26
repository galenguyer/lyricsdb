FROM python:3.8-alpine
MAINTAINER Galen Guyer <galen@galenguyer.com>

RUN mkdir /opt/lyricsdb

ADD requirements.txt /opt/lyricsdb

WORKDIR /opt/lyricsdb

RUN pip install -r requirements.txt

ADD . /opt/lyricsdb

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["gunicorn", "lyricsdb:APP", "--bind=0.0.0.0:8080", "--access-logfile=-"]
