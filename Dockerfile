FROM python:3.10-alpine

VOLUME /mnt/input
VOLUME /mnt/output

ENV CRON ""
ENV OPTIONS ""

COPY . /opt/phockup

RUN apk --no-cache add exiftool \
    && pip install --no-cache-dir -r /opt/phockup/requirements.txt \
    && ln -s /opt/phockup/phockup.py /usr/local/bin/phockup \
    && apk add bash \
    && apk add flock \
	&& apk add util-linux-login

RUN ["chmod", "-R", "a+rx", "/opt/phockup/"]

ENTRYPOINT ["/opt/phockup/entrypoint.sh"]
