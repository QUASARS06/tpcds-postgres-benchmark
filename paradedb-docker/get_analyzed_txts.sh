#!/bin/bash

# === CONFIGURATION ===
HOSTNAME=host.docker.internal
PORT=5432
USERNAME=chiragjain
DBNAME=tpcds

QLOC=/proj/tpcds_queries/acqueries
TXTLOC=/proj/tpcds_txts              # Output location for results

mkdir -p "$TXTLOC"

# === EXECUTION LOOP ===
for i in {1..99}; do
  echo "Running query $i..."
  QUERY_FILE="$QLOC/query${i}.sql"
  OUT_FILE="$TXTLOC/q${i}a.txt"

  if [ -f "$QUERY_FILE" ]; then
    psql -h "$HOSTNAME" -p "$PORT" -U "$USERNAME" -d "$DBNAME" -f "$QUERY_FILE" > "$OUT_FILE"
  else
    echo "Missing file: $QUERY_FILE"
  fi
done

echo "All queries executed. Results saved to: $TXTLOC"
