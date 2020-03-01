FROM ubuntu
RUN apt-get update
RUN apt-get install python3 libimage-exiftool-perl curl -y
RUN curl -L https://github.com/ivandokov/phockup/archive/latest.tar.gz -o phockup.tar.gz
RUN tar -zxf phockup.tar.gz
RUN mv phockup-* /opt/phockup
RUN ln -s /opt/phockup/phockup.py /usr/local/bin/phockup

# put your photos in "priginals" and they eill be copied sorted in "sorted"
CMD ["phockup", "originals", "sorted"]
