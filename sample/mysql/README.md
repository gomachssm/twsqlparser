# How to try sample program.

```shell script
# cd to this directory
cd sample/postgres
# run containers
docker-compose up -d
# execute sample program using sqlalchemy with mysql-connector-python
docker-compose exec py python sample_sqlalchemy.py
```