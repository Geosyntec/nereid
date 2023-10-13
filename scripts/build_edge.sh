set -e
export COMPOSE_FILE=docker-stack.yml
export COMPOSE_DOCKER_CLI_BUILD=1

docker compose \
-f docker-compose.shared.depends.yml \
-f docker-compose.shared.env.yml \
-f docker-compose.shared.volumes.yml \
-f docker-compose.shared.ports.yml \
-f docker-compose.edge.build.yml \
-f docker-compose.dev.yml \
config > docker-stack.yml
