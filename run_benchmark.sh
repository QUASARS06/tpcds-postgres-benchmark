#!/bin/bash

echo "📁 Step 1: Navigating to /proj/tpcds-postgres..."
cd /proj/tpcds-postgres || exit 1

echo "⚙️  Step 2: Running tpcds_generator.sh (compile, create schema, generate data, load DB, generate queries)..."
bash ./tpcds_generator.sh
echo "✅ Finished generating and loading TPC-DS data."

echo "📁 Step 3: Navigating to /proj/tpcds_queries..."
cd /proj/tpcds_queries || exit 1

echo "🧩 Step 4: Splitting query_0.sql into individual query files..."
python3 /proj/tpcds-postgres/split_sqls.py
echo "✅ Split complete: query1.sql to query99.sql created."

echo "🔍 Step 5: Creating EXPLAIN ANALYZE versions of queries..."
python3 /proj/tpcds-postgres/split_analyzing_sqls.py
echo "✅ Analyze queries created successfully."

echo "🕒 Step 6: Running all queries and capturing EXPLAIN ANALYZE output... (will run for long time)"
bash /proj/tpcds-postgres/get_analyzed_txts.sh
echo "✅ All queries executed. EXPLAIN ANALYZE output saved."

echo "📊 Step 7: Generating visual analysis plot (PDF + PNG)..."
python3 /proj/tpcds-postgres/analyze_explains_offline.py
echo "✅ Plot generated at /proj/tpcds_operator_breakdown_offline.pdf and .png"

echo "🎉 All steps completed successfully!"
