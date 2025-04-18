#! /usr/bin/env sh

set -e
source .env
az acr login --name $ACR_SERVER
