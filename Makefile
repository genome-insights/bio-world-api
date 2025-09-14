.PHONY: up down logs build

up:
\tdocker compose -f deploy/docker-compose.dev.yml up -d --build

down:
\tdocker compose -f deploy/docker-compose.dev.yml down -v

logs:
\tdocker compose -f deploy/docker-compose.dev.yml logs -f --tail=200

build:
\tdocker compose -f deploy/docker-compose.dev.yml build
