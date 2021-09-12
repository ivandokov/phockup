FROM python:3.9-alpine

RUN  apk add --no-cache --virtual .build-dependencies \
        curl \
    && apk --no-cache add exiftool \
    && curl -L https://github.com/ivandokov/phockup/archive/latest.tar.gz -o phockup.tar.gz \
    && tar -zxf phockup.tar.gz \
    && mv phockup-* /opt/phockup \
    && pip install --no-cache-dir --use-feature=2020-resolver -r /opt/phockup/requirements.txt \
    && ln -s /opt/phockup/phockup.py /usr/local/bin/phockup \
    && apk del --no-cache --purge .build-dependencies \
    && rm phockup.tar.gz

ENTRYPOINT [ "phockup" ]
