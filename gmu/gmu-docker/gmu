#!/bin/bash
#
# Script to launch the CommandlineMigrationClient.jar
#

function nojava() {
    echo "Please ensure \"java\" is in the PATH, set JAVA_HOME or run with --jdk option."
    exit 1
}

function ensure_JDK() {
    if [ ! -z "${1}" ] ; then
        EJ_javaver=$("${JAVA_HOME}/bin/java" -version 2>&1 | awk -F\" '/version/ {print $2}' | awk -F\. '{print $1"."$2}');

        EJ_want_major=$(echo "${1}" | awk -F'.' '{print $1}')
        EJ_want_minor=$(echo "${1}" | awk -F'.' '{print $2}')
        EJ_javaver_major=$(echo "${EJ_javaver}" | awk -F'.' '{print $1}')
        EJ_javaver_minor=$(echo "${EJ_javaver}" | awk -F'.' '{print $2}')

        if [ "${EJ_want_major}" -gt "${EJ_javaver_major}" ] ; then
            echo "Java ${1} is required, but ${EJ_javaver} was found."
            exit 1
        fi

        if [ "${EJ_want_major}" -eq "${EJ_javaver_major}" ] && [ "${EJ_want_minor}" -gt "${EJ_javaver_minor}" ]; then
            echo "Java ${1} is required, but ${EJ_javaver} was found."
            exit 1
        fi

        unset EJ_javaver EJ_want_major EJ_want_minor EJ_javaver_major EJ_javaver_minor
    fi
}

#
# Process script args
#
if [ "$1" == "--jdk" ]; then
    shift
    if [ -f "$1" ] && [ -x "$1" ] ; then
        JAVA_HOME="$(dirname $1)/.."
    elif [ -x "$1/bin/java" ]; then
        JAVA_HOME="$1"
    else
        nojava
    fi
    shift
fi

#
# Validate Java settings
#
if [ ! -z "${JAVA_HOME}" ] ; then
    if [ ! -x "${JAVA_HOME}/bin/java" ] ; then
        nojava
    fi
elif [ ! -z "${SSG_JAVA_HOME}" ] ; then
    JAVA_HOME="${SSG_JAVA_HOME}"
else
    JAVA="$(which java 2>/dev/null)"
    if [ $? -ne 0 ] ; then
        nojava
    else
        JAVA_HOME="$(dirname ${JAVA})/.."
    fi
fi
ensure_JDK 1.8

#
# Run client
#
"${JAVA_HOME}/bin/java" ${JAVA_OPTS} -DGMU_HOME="$(dirname "$0")" -jar   "$(dirname "$0")/GatewayMigrationUtility.jar" "$@"
