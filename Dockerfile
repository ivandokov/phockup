FROM python:3.8.7-alpine

RUN apk --no-cache add exiftool curl \
    && curl -L https://github.com/ivandokov/phockup/archive/latest.tar.gz -o phockup.tar.gz \
    && tar -zxf phockup.tar.gz \
    && mv phockup-* /opt/phockup \
    && ln -s /opt/phockup/phockup.py /usr/local/bin/phockup
