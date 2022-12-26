FROM python:3.8-alpine

# create user `eyetrack` and add it to group `eyetrack`
RUN addgroup -S eyetrack && adduser -S -G eyetrack eyetrack

# create logs directory and add logrotate rule
RUN mkdir /var/log/eyetrack
COPY docker/logrotate/eyetrack /etc/logrotate.d/

# assign permissions to `eyetrack`
RUN chown eyetrack:eyetrack /var/log/eyetrack

ARG dev

ENV IS_DEV_ENV=${dev:+dev-requirements.txt}

ENV REQUIREMENTS=${IS_DEV_ENV:-requirements.txt}

RUN pip install -U pip setuptools pipenv

COPY Pipfile* ./

# install python requirements
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc linux-headers postgresql-dev \
    musl-dev libffi-dev openssl-dev cargo jpeg-dev \
    freetype-dev zlib-dev \
    && pipenv requirements > requirements.txt \
    && pipenv requirements --dev > dev-requirements.txt \
    && pip uninstall --yes pipenv \
    && pip install -r ${REQUIREMENTS} \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

# set envirnoment variables
ENV SRC=timing_services
ENV USER_HOME=/home/eyetrack
ENV CODE_DIR=$USER_HOME/$SRC

WORKDIR $CODE_DIR

# copy all the code
COPY . $CODE_DIR

RUN chown -R eyetrack:eyetrack $CODE_DIR

USER eyetrack

ENTRYPOINT ["python3", "manage.py"]
