#!/bin/bash

./GatewayMigrationUtility.sh migrateOut --host gateway-dev --username admin --plaintextPassword password --trustCertificate --dest sample_export.xml --encryptionPassphrase @file:encryptm.txt --policyName "/ziggo/buildingBlocks/BB - R2 - Routing HTTPs - REST - v1"
