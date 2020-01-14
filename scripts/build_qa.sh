set -e

docker-compose \
-f docker-compose.shared.depends.yml \
-f docker-compose.qa.build.yml \
-f docker-compose.qa.ports.yml \
-f docker-compose.qa.env.yml \
config > docker-stack.yml

docker-compose -f docker-stack.yml build