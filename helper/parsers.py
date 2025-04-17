# parsers.py
import argparse

def get_citus_parser():
    """Returns the parser for the Citus extension."""
    citus_parser = argparse.ArgumentParser(prog="citus", add_help=False)
    citus_parser.add_argument("--workers", type=int, default=2)
    citus_parser.add_argument("--user", default="postgres")
    citus_parser.add_argument("--password", default="citusPass")
    citus_parser.add_argument("--db", default="citus_db")
    citus_parser.add_argument("--output", default="docker-compose.yml")
    return citus_parser

def get_paradedb_parser():
    """Returns the parser for the ParadeDB extension."""
    parade_parser = argparse.ArgumentParser(prog="paradedb", add_help=False)
    parade_parser.add_argument("--output", default="docker-compose.yml")
    return parade_parser
