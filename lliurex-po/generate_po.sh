#!/bin/bash

PYTHON_FILES="../python3/appconfig/*.py"
APP_NAME=python3-appconfig
PO_FILE=${APP_NAME}/${APP_NAME}.pot

mkdir -p $APP_NAME

xgettext $PYTHON_FILES -o $PO_FILE

