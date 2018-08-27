#!/bin/bash

# export service         
# 53270198e958cd5c497538aa06eebd86        ziggo/services/BSL/REST/BSLREST - CES8
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/services/bslrest.xml --service 53270198e958cd5c497538aa06eebd86

# export folders
# ziggo
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/folders/ziggo.xml --folder a18e10ad11b997e54716aa3907698dfe

# services
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/folders/services.xml --folder 53270198e958cd5c497538aa06eebc7c

# BSL
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/folders/bsl.xml --folder 53270198e958cd5c497538aa06eebcc2

# REST
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/folders/rest.xml --folder 53270198e958cd5c497538aa06eebd07
