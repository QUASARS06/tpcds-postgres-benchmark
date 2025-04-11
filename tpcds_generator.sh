#!/bin/bash

set -e
BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)
. "$BASEDIR/pgtpcds_defaults"

mkdir -p "$Q0DIR"
mkdir -p "$TPCDSTMP"

cd "$TPCDSDIR/tools"

# Step 0: Build tools if they don't exist
if [ ! -f "./dsdgen" ]; then
  echo "Building TPC-DS tools..."
  make CC=gcc-9
fi

# Step 1: Create schema in remote Postgres
echo "Creating TPC-DS schema in PostgreSQL..."
psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DATABASE" -f ./tpcds.sql

# Step 2: Generate data files
echo "Generating TPC-DS data..."
./dsdgen -FORCE -VERBOSE -SCALE $SCALE

# Step 3: Load data into PostgreSQL
for file in *.dat; do
  table=${file%.dat}
  echo "Loading $table..."

  sed 's/|$//' "$file" > "$Q0DIR/$file"

  if [[ "$file" == "customer.dat" ]]; then
    python3 "$BASEDIR/fix_encoding.py" --filename="$Q0DIR/$file"
  fi

  psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DATABASE" -q -c "TRUNCATE $table"
  psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DATABASE" -c "\copy $table FROM '${Q0DIR}/$file' CSV DELIMITER '|'"
done

# Step 4: Vacuum + analyze
echo "Running vacuum and analyze..."
psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DATABASE" -c "VACUUM FREEZE"
psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DATABASE" -c "ANALYZE"

# Step 5: Generate benchmark queries
echo "Generating queries using dsqgen..."
./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -VERBOSE Y -QUALIFY Y -DIALECT netezza -SCALE $SCALE -OUTPUT_DIR $Q0DIR

echo "Done! TPC-DS data and queries are ready in: $Q0DIR"
