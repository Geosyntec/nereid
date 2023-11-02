set -e
export COMPOSE_FILE=docker-stack.yml
export COMPOSE_DOCKER_CLI_BUILD=1

docker compose \
-f docker-compose.build.yml \
-f docker-compose.edge.build.yml \
config > docker-stack.yml
