#!/usr/bin/python3
import geojson
import json
from turfpy.measurement import bbox
import os
import os.path
from pathlib import Path
import hashlib
import pycurl
import uuid

import requests
import shutil

# You must initialize logging, otherwise you'll not see debug output.

placesApiUrl='http://places-api/places'  

BBOXES_GEOJSON = "/data/osm/bboxes.geojson"
myUuid = uuid.uuid1()

with open(BBOXES_GEOJSON, 'wb') as f:
    c = pycurl.Curl()
    c.setopt(c.URL, placesApiUrl + '/data/world')
    c.setopt(c.HEADERFUNCTION, lambda header_line: print(header_line.decode('utf-8')))
    c.setopt(c.WRITEDATA, f)
    c.perform()
    if (c.getinfo(pycurl.HTTP_CODE) >= 400):
        print('HTTP/1.1 404 Not Found')
        print('Content-type: application/json')
        print('')
        exit(0)
    c.close()

with open(BBOXES_GEOJSON) as f:
    gj = geojson.load(f)

for feature in gj['features']:
    myGeojson = {
        "type": "FeatureCollection",
        "generator": "JOSM",
        "features": [feature]
    }

    # myGeojson = json.loads(myGeo)
    # myGeojson.features.append(feature)
    myBbox = bbox(myGeojson)
    myFeature = myGeojson['features'][0]
    myProperties = myFeature.properties
    country = myProperties['country'].lower().replace(" ", "_")
    myId = myProperties['id']
    os.makedirs("/data/osm/" + country, exist_ok=True)
    osmFile = "/data/osm/" + country + "/" + myId + ".osm"
    osmFileTmp = "/tmp/" + country + "_" + myId + "_" + str(myUuid) + ".osm"
    osmCksumFile = "/data/osm/" + country + "/" + myId + ".cksum"

#   print(bbox(myGeojson))
    id = myGeojson['features'][0]['properties']['id']

    updateRequested = False
    if (myProperties.update == "1m"):
        print('Update every:' + myProperties.update)
        updateRequested = True
    elif (not os.path.isfile(osmFile)):
        print('file does not exist yet:' + osmFile)
        updateRequested = True
    else:
        a_file = open(osmFile)
        line1 = a_file.readline()
        line2 = a_file.readline()
        if (not '<osm version=' in line2):
            print('file content is not OK:' + osmFile)
            updateRequested = True

    if (updateRequested):
        overpass = "https://overpass-api.de/api/map?bbox=" + \
            str(myBbox[0]) + "," + str(myBbox[1]) + "," + \
            str(myBbox[2]) + "," + str(myBbox[3])

        print("request: " + overpass)

        with open(osmFileTmp, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, overpass)
            c.setopt(c.HEADERFUNCTION, lambda header_line: print(header_line.decode('utf-8')))
            c.setopt(c.WRITEDATA, f)
            c.perform()
            if (c.getinfo(pycurl.HTTP_CODE) >= 400):
                print('HTTP/1.1 404 Not Found')
                print('Content-type: application/json')
                print('')
                exit(0)
            c.close()
        print("request done")

        a_file = open(osmFileTmp)
        line1 = a_file.readline()
        line2 = a_file.readline()
        if ('<osm version=' in line2):
            shutil.move(osmFileTmp, osmFile)
            # cksum
            osmContent = Path(osmFile).read_text()
            cksum = hashlib.md5(osmContent.encode('utf-8')).hexdigest()
            open(osmCksumFile, "w+").write(cksum)

            print("downloaded: " + osmFile)
            print("cksum: " + str(cksum))
        else:
            print("download failed")
    else:
        print(osmFile + " already downloaded")
