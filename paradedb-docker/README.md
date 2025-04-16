# tpcds-postgres-benchmark-paradedb

This includes the changes needed to run the tpcds benchmark on postgres + paradedb

# How to run

1. docker-compose up --build
2. docker exec -it paradedb psql -U paradedb_user -d tpcds-paradedb (to exec into paradeb)
3a. docker exec -it tpcds bash (to exec into the tpcds benchmark container)
3b. bash /proj/run_benchmark.sh