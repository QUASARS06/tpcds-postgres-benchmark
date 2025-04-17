# How to Run Citus

0. **Make sure Docker is installed and running** on your machine.

1. **Install dependencies**

```bash
python3 -m pip install jinja2
```

2. Generate the `docker-compose.yml` file from the template
```bash
python3 init-citus.py [--workers 2] [--user postgres] [--password citus_pass] [--db citus_db] [--output docker-compose.yml]
```

3. Run the Citus cluster
```bash
docker-compose up
```