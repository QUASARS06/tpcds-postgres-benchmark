# tpcds-postgres-benchmark

Dockerized the tpcds setup. Includes the scripts to compile the binaries, generate data, tables, queries, etc and load it into postgres running on Host. Has python code to fix the faulty generate sql files. Also included code to split the query0.sql into individual query files. Has python script to analyze the output after running the queries and generate plots.

Most of the bash and python scripts mentioned above are copied over from - https://github.com/celuk/tpcds-postgres?tab=readme-ov-file (they are modified for simplicity using chatgpt)

# How to run

0. Update the PGHOST and PGUSER in Dockerfile and pgtpcds_defaults file as per your settings. Optionally update SCALE to generate data appropriately (n = n GB of data, eg 1=1GB, 100=100GB, should be integer)
1. Make sure to create a database on postgres - CREATE DATABASE tpcds;
2. docker compose up
3. Exec into docker:- docker exec -it bigdata bash
4. bash /proj/run_benchmark.sh

OR you can run each step individually

4. cd /proj/tpcds-postgres
5. bash /proj/tpcds-postgres/tpcds_generator.sh
6. cd /proj/tpcds_queries
7. python3 /proj/tpcds-postgres/split_sqls.py
8. python3 /proj/tpcds-postgres/split_analyzing_sqls.py
9. bash /proj/tpcds-postgres/get_analyzed_txts.sh (this will take very long to run)
10. python3 /proj/tpcds-postgres/run_tpcds_visual_analysis.py (the pdf and png of plot will be stored at /proj)
