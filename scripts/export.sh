#!/bin/bash

# Set the field separator to new line
IFS=$'\n'
# Types are:
# POLICY, SERVICE, FOLDER
EXPORT_TYPE="SERVICE"
EXPORT_LIST=`./GatewayMigrationUtility.sh list --host gateway-dev --port 8443 --username admin --plaintextPassword password --trustCertificate --type $EXPORT_TYPE | awk -F$'\t' '{print $1}'`

# export the shit
for i in $EXPORT_LIST
do
	echo $i

	# export services
	if [ $EXPORT_TYPE == "SERVICE" ]
	then
		./GatewayMigrationUtility.sh migrateOut --host gateway-dev --username admin --plaintextPassword password --trustCertificate --dest "exports/services/$i" --encryptionPassphrase @file:encryptm.txt --service "$i"
	fi

	# export policies
	if [ $EXPORT_TYPE == "POLICY" ]
	then
		./GatewayMigrationUtility.sh migrateOut --host gateway-dev --username admin --plaintextPassword password --trustCertificate --dest "exports/policies/$i" --encryptionPassphrase @file:encryptm.txt --policy "$i"
	fi

	# export folders
	if [ $EXPORT_TYPE == "FOLDER" ]
	then
		./GatewayMigrationUtility.sh migrateOut --host gateway-dev --username admin --plaintextPassword password --trustCertificate --dest "exports/folders/$i" --encryptionPassphrase @file:encryptm.txt --folder "$i"
	fi

done
