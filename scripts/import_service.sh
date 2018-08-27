#!/bin/bash

# export service         
# 53270198e958cd5c497538aa06eebd86        ziggo/services/BSL/REST/BSLREST - CES8
./GatewayMigrationUtility.sh migrateOut --trustCertificate --argFile argFile.properties --dest exports/services/bslrest.xml --service 53270198e958cd5c497538aa06eebd86

# import folder ziggo/services/BSL/REST
./GatewayMigrationUtility.sh migrateIn --argFile argFile.properties --bundle exports/folders/ziggo.xml --results results.xml --trustCertificate
./GatewayMigrationUtility.sh migrateIn --argFile argFile.properties --bundle exports/folders/services.xml --results results.xml --trustCertificate
./GatewayMigrationUtility.sh migrateIn --argFile argFile.properties --bundle exports/folders/bsl.xml --results results.xml --trustCertificate
./GatewayMigrationUtility.sh migrateIn --argFile argFile.properties --bundle exports/folders/rest.xml --results results.xml --trustCertificate

# import service ziggo/services/BSL/REST/BSLREST - CES8
#./GatewayMigrationUtility.sh migrateIn --argFile argFile.properties --bundle exports/services/bslrest.xml --results results.xml --trustCertificate
