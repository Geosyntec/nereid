set -e
export COMPOSE_FILE=docker-stack.yml

docker-compose \
-f docker-compose.shared.depends.yml \
-f docker-compose.shared.admin.yml \
-f docker-compose.shared.env.yml \
-f docker-compose.shared.volumes.yml \
-f docker-compose.dev.ports.yml \
-f docker-compose.edge.build.yml \
config > docker-stack.yml

docker-compose -f docker-stack.yml build