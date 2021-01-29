# How to try sample program.

```shell script
# cd to this directory
cd sample/postgres
# run containers
docker-compose up -d
# execute sample program using pg8000
docker-compose exec py python sample_pg8000.py
```