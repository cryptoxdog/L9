admin@L9:~$ cd /opt/l9 && cat docker-compose.yml | head -30

version: "3.9"

services:

api:

build: .

env_file: .env

command: uvicorn api.main:app --host 0.0.0.0 --port 8000

depends_on:

- postgres

- redis

- qdrant

- neo4j

ports:

- "127.0.0.1:8000:8000"

slack:

build: .
