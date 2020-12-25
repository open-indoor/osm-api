FROM caddy:2-alpine

RUN apk add --update-cache \
    bash \
    wget \
    procps \
    curl \
    vim \
    util-linux \
    jq \
    gettext \
    python3 py3-pip geos geos-dev py3-wheel py3-scipy curl-dev gcc musl-dev \
    && rm -rf /var/cache/apk/*

COPY ./requirements.txt /osm/
RUN pip install -r /osm/requirements.txt

COPY ./Caddyfile /tmp/Caddyfile

WORKDIR /usr/bin
COPY ./action.py /usr/bin/action
COPY ./tic.sh /usr/bin/tic
COPY ./osm-api.sh /osm/osm-api.sh
RUN chmod +x /osm/osm-api.sh

CMD /osm/osm-api.sh

EXPOSE 80
