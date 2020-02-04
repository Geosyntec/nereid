set -e

docker-compose \
-f docker-compose.shared.depends.yml \
-f docker-compose.dev.build.yml \
-f docker-compose.dev.ports.yml \
-f docker-compose.dev.env.yml \
config > docker-stack.yml

docker-compose -f docker-stack.yml build