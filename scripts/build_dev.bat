
set COMPOSE_FILE=docker-stack.yml

call docker-compose ^
-f docker-compose.shared.depends.yml ^
-f docker-compose.shared.admin.yml ^
-f docker-compose.shared.env.yml ^
-f docker-compose.shared.volumes.yml ^
-f docker-compose.dev.volumes.yml ^
-f docker-compose.dev.env.yml ^
-f docker-compose.dev.ports.yml ^
-f docker-compose.dev.build.yml ^
config > docker-stack.yml

docker-compose -f docker-stack.yml build
