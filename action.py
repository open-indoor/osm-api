#!/usr/bin/python3

# apply getOsm \
#     --bounds BulgariaHaskovoXackoboGeorgiKirkovStreet_bounds.geojson \
#     --output BulgariaHaskovoXackoboGeorgiKirkovStreet.osm

# apply filter \
#     --input BulgariaHaskovoXackoboGeorgiKirkovStreet.osm \
#     --bounds BulgariaHaskovoXackoboGeorgiKirkovStreet_bounds.geojson \
#     --output BulgariaHaskovoXackoboGeorgiKirkovStreet_filtered.osm

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
import sys
import getopt
from shapely.geometry import shape, mapping, Polygon

import geopandas
# You must initialize logging, otherwise you'll not see debug output.

def getOsm(myGeojson):
    myUuid = uuid.uuid1()

    myBbox = bbox(myGeojson)
    myFeature = myGeojson['features'][0]
    myProperties = myFeature['properties']
    country = myProperties['country'].lower().replace(" ", "_")
    myId = myProperties['id']
    os.makedirs("/data/osm/" + country, exist_ok=True)
    osmFile = "/data/osm/" + country + "/" + myId + ".osm"
    osmFileTmp = "/tmp/" + country + "_" + myId + "_" + str(myUuid) + ".osm"
    osmFileFiltered = "/tmp/" + country + "_" + myId + "_" + str(myUuid) + "_filtered.osm"
    bounds_file = "/tmp/" + country + "_" + myId + "_" + str(myUuid) + "_bounds.geojson"
    osmCksumFile = "/data/osm/" + country + "/" + myId + ".cksum"
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
        try:
            overpass_request = requests.get(overpass)
            with open(osmFileTmp, 'wb') as osm_file_tmp:
                osm_file_tmp.write(overpass_request.content)
        except:
            sys.exit("Cannot get osm")
        a_file = open(osmFileTmp)
        line1 = a_file.readline()
        line2 = a_file.readline()
        if ('<osm version=' in line2):
            shutil.move(osmFileTmp, osmFile)
            # os.rename(osmFileTmp, osmFile)
            # Filter with bound
            with open(bounds_file, 'w') as outfile:
                json.dump(myGeojson, outfile, ensure_ascii=False)
            filter(osmFile, bounds_file, osmFileFiltered)
            shutil.move(osmFileFiltered, osmFile)
            # os.rename(osmFileFiltered, osmFile)
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

def filter(input_fn, bounds_fn, output_fn):
    print('********** filter **********')
    with open(bounds_fn) as f:
        bounds_geojson = json.load(f)
    feature = bounds_geojson["features"][0]
    geometry = Polygon(shape(feature['geometry']))
    # geojson_bounds = json.loads(geopandas.GeoSeries([geometry.convex_hull]).to_json())
    # print(json.dumps(geometry.__geo_interface__))
    bounds_geojson["features"][0]['geometry'] = json.loads(json.dumps(geometry.__geo_interface__, ensure_ascii=False))
    with open(bounds_fn, 'w') as outfile:
        json.dump(bounds_geojson, outfile, ensure_ascii=False)

    cmd = ('osmium extract -p ' + bounds_fn + ' ' + input_fn + ' -o ' + output_fn)
    print('starting cmd: ' + cmd)
    os.system(cmd)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[2:], "b:i:o:", ["bounds=", "input=", "output="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
        bounds_fn = None
        input_fn = None
        output_fn = None
    for o, a in opts:
        if o in ("-b", "--bounds"):
            bounds_fn = a
        elif o in ("-i", "--input"):
            input_fn = a
        elif o in ("-o", "--output"):
            output_fn = a
        else:
            print(o)
            print(a)
            assert False, "unhandled option"
    action = sys.argv[1] if len(sys.argv) > 1 else None

    if action == "getOsm":
        with open(bounds_fn) as json_file:
            my_geojson = json.load(json_file)
        getOsm(my_geojson)
    elif action == "filter":
        filter(input_fn, bounds_fn, output_fn)
    else:
        placesApiUrl='http://places-api/places'  
        BBOXES_GEOJSON = "/data/osm/bboxes.geojson"
        try:
            places_request = requests.get(placesApiUrl + '/data/world')
            gj = places_request.json()
            with open(BBOXES_GEOJSON, 'wb') as bboxes_geojson:
                bboxes_geojson.write(places_request.content)
        except:
            sys.exit("Cannot get places")

        for feature in gj['features']:
            myGeojson = {
                "type": "FeatureCollection",
                "generator": "JOSM",
                "features": [feature]
            }
            getOsm(myGeojson)

if __name__ == "__main__":
    main()

