import os
import re
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# === Configuration ===
TXT_DIR = "/proj/tpcds_txts"
OUTPUT_IMG = "/proj/tpcds_operator_breakdown_offline.png"
OUTPUT_PDF = "/proj/tpcds_operator_breakdown_offline.pdf"

functions = [
    "Hash Join", "Nested Loop", "Merge Join", "Hash",
    "Seq Scan", "Index Scan", "Bitmap Heap Scan", "Bitmap Index Scan",
    "Sort", "Aggregate", "CTE Scan", "Materialize", "Gather", "Gather Merge",
    "Subquery Scan", "Unique", "Limit", "Other"
]
colors = [
    "blue", "green", "red", "cyan", "magenta", "orange", "#A020F0", "#8B4513",
    "#5F9EA0", "#FF6347", "#2E8B57", "#D2691E", "#6495ED", "#FFD700", "#DA70D6",
    "#20B2AA", "#F4A460", "gray"
]

# === Regex Patterns ===
operator_re = re.compile(r"^\s*(?:->)?\s*([A-Za-z ]+?)\s+\(.*?actual time=([\d\.]+)\.\.([\d\.]+) rows=")
execution_re = re.compile(r"Execution Time: ([\d\.]+) ms")

# === Data Structures ===
ylist = [[0 for _ in range(99)] for _ in functions]
maxylist = []
maxnamelist = []
xlist = []

for qid in range(1, 100):
    t_start = time.time()
    file_path = os.path.join(TXT_DIR, f"q{qid}a.txt")
    if not os.path.isfile(file_path):
        print(f"❌ Missing {file_path}")
        maxylist.append(0)
        maxnamelist.append("missing")
        continue

    with open(file_path, "r") as f:
        lines = f.readlines()

    exec_time = 0
    operator_times = {}

    for line in lines:
        # Skip long filter/parameter dump lines for performance
        if len(line) > 1000:
            continue

        # Fast path: extract execution time
        exec_match = execution_re.search(line)
        if exec_match:
            exec_time = float(exec_match.group(1))
            continue

        # Parse operator node
        try:
            if "actual time=" not in line or "rows=" not in line:
                continue

            match = operator_re.search(line)
            if match:
                op = match.group(1).strip()
                start, end = float(match.group(2)), float(match.group(3))
                duration = max(end - start, 0)
                op_key = op if op in functions else "Other"
                operator_times[op_key] = operator_times.get(op_key, 0) + duration
        except Exception as e:
            print(f"⚠️  Error parsing line in Q{qid}: {e}")
            continue

    if exec_time == 0:
        print(f"⚠️  No execution time for Q{qid}")
        maxylist.append(0)
        maxnamelist.append("invalid")
        continue

    xlist.append(str(qid))
    max_func = "Other"
    max_pct = 0

    for i, func in enumerate(functions):
        op_time = operator_times.get(func, 0)
        pct = (op_time / exec_time) * 100
        ylist[i][qid - 1] = pct

        if pct > max_pct:
            max_pct = pct
            max_func = func

    maxylist.append(max_pct)
    maxnamelist.append(max_func)

    print(f"✅ Processed query {qid} in {time.time() - t_start:.2f}s")

# === Normalize to 100% if needed
for i in range(99):
    total = sum(ylist[j][i] for j in range(len(functions)))
    if total > 100:
        for j in range(len(functions)):
            ylist[j][i] = (ylist[j][i] / total) * 100

# === Plotting
plt.rcParams["font.size"] = 18
plt.figure(figsize=(32, 18))

bars1 = plt.bar(xlist, ylist[0], color=colors[0])
cum = np.array(ylist[0])
for i in range(1, len(functions)):
    plt.bar(xlist, ylist[i], color=colors[i], bottom=cum)
    cum += np.array(ylist[i])

# Add % labels
for idx, bar in enumerate(bars1):
    plt.text(bar.get_x() + bar.get_width()/2, 110, f"%{maxylist[idx]:.1f}", ha='center', va='center', fontsize=14, rotation='vertical')

plt.title("TPC-DS Operator Time Breakdown (Offline)", fontsize=28)
plt.xlabel("Query ID", fontsize=24)
plt.ylabel("Time Contribution (%)", fontsize=24)
plt.xticks(rotation=75)
plt.grid(True)

patches = [mpatches.Patch(color=colors[i], label=functions[i]) for i in range(len(functions))]
plt.legend(handles=patches, loc="upper left", bbox_to_anchor=(1, 1), fontsize=18)

plt.tight_layout()
plt.savefig(OUTPUT_PDF)
plt.savefig(OUTPUT_IMG)

print("✅ Offline chart generated:")
print(f"📄 PDF: {OUTPUT_PDF}")
print(f"🖼️  PNG: {OUTPUT_IMG}")
