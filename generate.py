#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
from helper.parsers import get_citus_parser, get_paradedb_parser
import argparse
import subprocess
import time
import os

CITUS_CMD="citus"
PARADE_CMD="paradedb"

def generate_citus(args):
    abspath = os.getcwd()
    print(f"Generating Citus cluster with {args.workers} workers")
    env = Environment(loader=FileSystemLoader('./citus-docker/templates/'))
    template = env.get_template('docker-compose.j2')

    print(f"the password is {args.password}")
    print(f"the user is {args.user}")
    print(f"the db is {args.db}")
    print(f"the num_workers is {args.workers}")

    rendered = template.render(
        postgres_user=args.user,
        postgres_password=args.password,
        postgres_db=args.db,
        num_workers=args.workers,
        init_path=f"{abspath}/citus-docker/init.sql"
    )

    with open(f"{abspath}/citus-docker/docker-compose.yml", "w") as f:
        f.write(rendered)

    print("✅ docker-compose.yml generated.")

    init_template = template = env.get_template('init.j2')
    ren = init_template.render(
        num_workers=args.workers
    )
    with open(f"{abspath}/citus-docker/init.sql", "w") as f:
        f.write(ren)

    print("Creating the Citus cluster")

    try:
        # Run Docker Compose in the background to start the services
        subprocess.Popen(f'cd {abspath}/citus-docker && docker-compose up -d', shell=True)
        print("✅ Docker Compose started in the background.")

        # Wait for a few seconds to ensure the services are up (you can improve this with checks)
        time.sleep(5)

        # Trigger the Citus initialization
        # psql command to add workers to the coordinator (you can replace this with your actual setup commands)
        # print("Initializing Citus cluster...")
        # for w in range(args.workers):
        #     subprocess.run(
        #         f'docker exec -i citus-coordinator psql -U postgres -c "SELECT citus_add_node(\'worker{w}\', 5432);"', 
        #         shell=True,
        #         check=True
        #     )

        # print("✅ Citus workers added to coordinator.")

        # # If you have a distributed table to create, you can add that too
        # # Example of creating a distributed table:
        # subprocess.run(
        #     f'cd {abspath}/citus-docker && docker exec -i citus-coordinator psql -U postgres -c "SELECT citus.create_distributed_table(\'your_table_name\', \'column_name\');"',
        #     shell=True,
        #     check=True
        # )

        # print("✅ Distributed table created.")
        
    except Exception as e:
        print(f"Error creating Citus cluster: {e}")

def generate_paradedb(args):
    print("Generating ParadeDB setup")
    # Jinja rendering logic for ParadeDB here...
    pass

num_workers=2
postgres_user="postgres"
postgres_password="pgPass123"
postgres_db="citusdb"
output_file="thisfile.txt"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate docker-compose setups for different extensions")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Get the parsers for different extensions
    citus_parser = get_citus_parser()
    parade_parser = get_paradedb_parser()

    # Add subparsers to the main parser
    subparsers.add_parser("citus", parents=[citus_parser], help="Generate config for Citus").set_defaults(func=generate_citus)
    subparsers.add_parser("paradedb", parents=[parade_parser], help="Generate config for ParadeDB").set_defaults(func=generate_paradedb)

    # Generate the Docker compose files
    args = parser.parse_args()
    args.func(args)