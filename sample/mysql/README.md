# How to try sample program.

```shell script
# cd to this directory
cd sample/mysql

# run containers
docker-compose up -d

# execute sample program using sqlalchemy with mysql-connector-python
# If error "ModuleNotFoundError: No module named 'sqlalchemy'" occurs, wait a few tens of seconds and try again.
docker-compose exec py python sample_sqlalchemy.py

# exit containers
docker-compose down
```