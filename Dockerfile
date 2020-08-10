FROM python:latest

RUN apt-get update -y
RUN apt-get install apt-utils -y
RUN apt-get install libimage-exiftool-perl -y
RUN curl -L https://github.com/ivandokov/phockup/archive/latest.tar.gz -o phockup.tar.gz
RUN tar -zxf phockup.tar.gz
RUN mv phockup-* /opt/phockup
RUN ln -s /opt/phockup/phockup.py /usr/local/bin/phockup
