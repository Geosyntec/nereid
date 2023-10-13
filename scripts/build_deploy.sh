set -e
export COMPOSE_FILE=docker-stack.yml
export COMPOSE_DOCKER_CLI_BUILD=1

docker compose \
-f docker-compose.shared.depends.yml \
-f docker-compose.shared.env.yml \
-f docker-compose.shared.volumes.yml \
-f docker-compose.shared.ports.yml \
-f docker-compose.shared.build.yml \
-f docker-compose.deploy.images.yml \
config > docker-stack.yml
