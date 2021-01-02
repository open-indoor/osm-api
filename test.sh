#!/bin/bash

set -x
set -e
docker build \
    --label openindoor/osm-api \
    -t openindoor/osm-api .

docker run \
    -v $(pwd)/test/data:/data \
    -v $(pwd)/test/test.sh:/osm/test \
    -v $(pwd)/action.py:/usr/bin/action \
    -it openindoor/osm-api \
    /osm/test