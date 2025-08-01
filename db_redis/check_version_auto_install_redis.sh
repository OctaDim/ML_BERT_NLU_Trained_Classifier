#!/bin/bash

REDIS_MIN_VERSION="6.2.0"
REDIS_INSTALLED=false

# Checking if Redis installed
if command -v redis-server &>/dev/null; then
    # Getting current Redis version
    REDIS_VERSION=$(redis-server --version | awk '{print $3}' | cut -d'=' -f2)

    # Comparing current Redis version with minimal required Redis version
    if [ "$(printf '%s\n' "$REDIS_MIN_VERSION" "$REDIS_VERSION" | sort -V | head -n1)" = "$REDIS_MIN_VERSION" ]; then
        echo "Redis version $REDIS_VERSION installed and satisfies minimal requirements (>= $REDIS_MIN_VERSION) [OK]"
        REDIS_INSTALLED=true
    else
        echo "REDIS VERSION $REDIS_VERSION INSTALLED, BUT THE MINIMAL REQUIRED VERSION IS >= $REDIS_MIN_VERSION [WARNING]"
    fi
else
    echo "Redis is installed [OK]"
fi

# Installing/updating Redis if redis is not installed or the version doesn't satisfy minimal requirements
if [ "$REDIS_INSTALLED" = false ]; then
    echo "INSTALLING REDIS PROCESS....."

    # For Ubuntu/Debian
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y redis-server
    # For CentOS/RHEL
    elif [ -f /etc/redhat-release ]; then
        yum install -y redis
    else
        echo "UNKNOWN LINUX DISTRIBUTIVE [ERROR]. PLEASE, INSTALL REDIS MANUALLY"
        exit 1
    fi

    # Checking if Redis installation is success
    if ! command -v redis-server &>/dev/null; then
        echo "REDIS INSTALLATION [ERROR]"
        exit 1
    fi

    # Checking Redis version after installation
    NEW_VERSION=$(redis-server --version | awk '{print $3}' | cut -d'=' -f2)
    if [ "$(printf '%s\n' "$REDIS_MIN_VERSION" "$NEW_VERSION" | sort -V | head -n1)" != "$REDIS_MIN_VERSION" ]; then
        echo "INSTALLED REDIS VERSION $NEW_VERSION IS NOT SATISFIES MINIMAL REQUIREMENTS YET [ERROR]"
        exit 1
    fi

    # Switching on auto-start and start service as daemon
    systemctl enable redis-server
    systemctl start redis-server

    # Waiting successful start of the redis server by pinging it
    COUNTER=0
    while ! redis-cli ping &>/dev/null && [ $COUNTER -lt 10 ]; do
        sleep 1
        COUNTER=$((COUNTER+1))
    done

    if ! redis-cli ping &>/dev/null; then
        echo "REDIS DIDN'T STARTED SUCCESSFULLY AFTER INSTALLATION [ERROR]"
        exit 1
    fi

    echo "REDIS INSTALLED AND STARTED SUCCESSFULLY [OK]"
fi

exit 0
