#! /usr/bin/env sh

set -e
source .env
az acr login --name $AZURE_CONTAINER_REGISTRY
