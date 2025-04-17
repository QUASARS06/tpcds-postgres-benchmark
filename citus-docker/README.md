# How to Run Citus

0. **Make sure Docker is installed and running** on your machine.

1. **Install dependencies**

```bash
python3 -m pip install jinja2
```

2. From the base directory, generate the `docker-compose.yml` file from the template for Citus
```bash
python3 generate.py citus [--workers 2] [--user postgres] [--password citus_pass] [--db citus_db] [--output docker-compose.yml]
```

3. The above commands should generate the `docker-compose.yml` file inside the `citus-docker` directory and trigger the citus cluster creation on the local node.