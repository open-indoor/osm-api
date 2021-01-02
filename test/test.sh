#!/bin/bash

action getOsm --bounds=/data/bulgaria/BulgariaHaskovoXackoboGeorgiKirkovStreet_bounds.geojson
action getOsm --bounds=/data/japan/JapanTokyoUniversityOfTechnology_bounds.geojson
action getOsm --bounds=/data/france/FranceRennesCFMIRennes2BatS_bounds.geojson
action getOsm --bounds=/data/france/FranceRennesCFMIRennes2LaPresidence_bounds.geojson
# action filter \
#     --input=/data/bulgaria/BulgariaHaskovoXackoboGeorgiKirkovStreet.osm \
#     --bounds=/data/bulgaria/BulgariaHaskovoXackoboGeorgiKirkovStreet_bounds.geojson \
#     --output=/data/bulgaria/BulgariaHaskovoXackoboGeorgiKirkovStreet_filtered.osm

# action filter \
#     --input=/data/france/FranceRennesCFMIRennes2BatS.osm \
#     --bounds=/data/france/FranceRennesCFMIRennes2BatS_bounds.geojson \
#     --output=/data/france/FranceRennesCFMIRennes2BatS_filtered.osm

# action filter \
#     --input=/data/france/FranceRennesCFMIRennes2LaPresidence.osm \
#     --bounds=/data/france/FranceRennesCFMIRennes2LaPresidence_bounds.geojson \
#     --output=/data/france/FranceRennesCFMIRennes2LaPresidence_filtered.osm
