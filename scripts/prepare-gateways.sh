#!/bin/bash
gmu migrateIn -z gmu/dev-argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo
gmu migrateIn -z gmu/tst-argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo
gmu migrateIn -z gmu/prd-argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo
