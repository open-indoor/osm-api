#!/bin/bash

# curl 'https://www.openstreetmap.org/api/0.6/map?bbox=2.35879,48.87601,2.36034,48.87759'
# wget 'https://www.openstreetmap.org/api/0.6/map?bbox=2.35787,48.87617,2.3614,48.87758'
# https://api.openindoor.io/osm/costa_rica/CostaRicaSanJoseStarbucks.osm

# https://api.openindoor.io/places/bboxes/world

set -x

# /usr/bin/flock /var/tmp/osm.lock /usr/bin/osm.sh

osmUpdate () {
  mkdir -p /data/osm
  uuid="$(uuidgen)"

  while read bbox; do
    myBbox=$(echo -e "${bbox}" | jq '.')
    id=$(echo "${myBbox}" | grep '"id":' | cut -d'"' -f4)
    country=$(echo -e "${myBbox}" | grep '"country":' | cut -d'"' -f4 | tr '[:upper:]' '[:lower:]' | sed 's/ /_/g')
    mkdir -p "/data/osm/${country}"
    osmfile="/data/osm/${country}/${id}.osm"
    osmfileTmp="/tmp/${country}_${id}_${uuid}.osm"
    osmcksum="/data/osm/${country}/${id}.cksum"
    update=$(echo "${myBbox}" | grep '"update":' | cut -d'"' -f4)
    town=$(echo "${myBbox}" | grep '"town":' | cut -d'"' -f4)
    place=$(echo "${myBbox}" | grep '"place":' | cut -d'"' -f4)
    lon1=$(echo "${myBbox}" | grep -A 1 '"bbox":' | tail -1 | sed 's/\s//g' | sed 's/,$//g')
    lat1=$(echo "${myBbox}" | grep -A 2 '"bbox":' | tail -1 | sed 's/\s//g' | sed 's/,$//g')
    lon2=$(echo "${myBbox}" | grep -A 3 '"bbox":' | tail -1 | sed 's/\s//g' | sed 's/,$//g')
    lat2=$(echo "${myBbox}" | grep -A 4 '"bbox":' | tail -1 | sed 's/\s//g' | sed 's/,$//g')

    if [ ! -f "${osmfile}" ] || ! grep -q '<osm version=' "${osmfile}" || [ "x${update}" = "x1m" ] ; then
      overpass="https://overpass-api.de/api/map?bbox=""$lon1"",""$lat1"",""$lon2"",""$lat2"
      echo $overpass
      curl -k -L $overpass > "${osmfileTmp}"
      if grep -q '<osm version=' "${osmfileTmp}" ; then
        mv -f "${osmfileTmp}" "${osmfile}"
        echo "downloaded"
      else
        echo "download failed"
      fi
    else
      echo "$f already downloaded"
    fi

    if [ -f "${osmfile}" ] \
    && grep -q '<osm version=' "${osmfile}"; then
      # Manage checksum
      cat "${osmfile}" \
      | sed 's/generator=\"Overpass API .*\"/generator=\"Overpass API\"/g' \
      | sed 's/osm_base=\".*\"/osm_base=\"\"/g' \
      | cksum \
      | cut -d " " -f1 \
      > "${osmcksum}"
    fi
  done <<< $(cat "${BBOXES_JSON}" | jq -c '.[]')
}

echo "osmUpdate"
osmUpdate