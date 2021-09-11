FROM python:3.9-alpine

COPY . /opt/phockup

RUN apk --no-cache add exiftool \
    && pip install --no-cache-dir --use-feature=2020-resolver -r /opt/phockup/requirements.txt \
    && ln -s /opt/phockup/phockup.py /usr/local/bin/phockup

ENTRYPOINT [ "phockup" ]
