# How to try sample program.

```shell script
# cd to this directory
cd sample/postgres

# run containers
docker-compose up -d

# execute sample program using pg8000
# If error "ModuleNotFoundError: No module named 'pg8000'" occurs, wait a few tens of seconds and try again.
docker-compose exec py python sample_pg8000.py

# execute sample program using sqlalchemy with psycopg2
# If error "ModuleNotFoundError: No module named 'pg8000'" occurs, wait a few tens of seconds and try again.
docker-compose exec py python sample_sqlalchemy.py

# exit containers
docker-compose down
```