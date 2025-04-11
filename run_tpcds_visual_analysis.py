import os
import subprocess
import re
import time
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# === Config Paths ===
ATXTS_PATH = "/proj/tpcds_txts/"
PLAN_TABLE_PATH = "/proj/tpcds_plan_tables/"
PFX = "q"
SFX = "a.txt"
PLAN_PFX = "qatable"
PLAN_SFX = ".txt"
CHART_BASE_NAME = "tpcds_runtime_profile"
TITLE = "TPC-DS Query Operator Breakdown (1GB)"

# === Plan Exporter Tool
PLAN_EXPORTER = "plan-exporter"  # should be in PATH

# === List of operators and colors ===
functions = [
    'Parallel Hash Join', 'Sort', 'Index Scan', 'Index Only Scan',
    'Parallel Seq Scan', 'Gather', 'Gather Merge', 'Bitmap Heap Scan',
    'CTE Scan', 'Partial HashAggregate', 'Seq Scan', 'HashAggregate',
    'Finalize GroupAggregate', 'MixedAggregate', 'Hash Join', 'Other'
]
colors = [
    'blue', 'green', 'red', '#F5DEB3', 'cyan', 'magenta', 'yellow',
    '#800000', '#FF8C00', '#00FF7F', '#4682B4', '#800080', '#8B4513',
    '#696969', '#808000', 'black'
]

# === Ensure output dir exists
os.makedirs(PLAN_TABLE_PATH, exist_ok=True)

# === Track data
xlist = []
ylist = [[0]*99 for _ in range(len(functions))]
maxylist = []
maxnamelist = []

# === Step 1: Upload and extract plans
for qid in range(1, 100):
    txt_file = os.path.join(ATXTS_PATH, f"{PFX}{qid}{SFX}")
    out_file = os.path.join(PLAN_TABLE_PATH, f"{PLAN_PFX}{qid}{PLAN_SFX}")

    if not os.path.exists(txt_file):
        print(f"❌ Missing: {txt_file}")
        maxylist.append(0)
        maxnamelist.append("empty")
        continue

    print(f"📤 Processing query {qid}...")

    # Upload to depesz
    try:
        upload_cmd = f"cat {txt_file} | {PLAN_EXPORTER} --target=depesz --auto-confirm"
        url_output = subprocess.check_output(upload_cmd, shell=True).decode()
        url = re.search(r'URL: (.*)', url_output).group(1) + "#stats"
    except Exception as e:
        print(f"⚠️  Upload failed for Q{qid}: {e}")
        maxylist.append(0)
        maxnamelist.append("upload_failed")
        continue

    # Fetch depesz page source
    try:
        wget_cmd = f"wget '{url}' -q -O -"
        html = subprocess.check_output(wget_cmd, shell=True).decode()

        # Fix invalid tags for parsing
        html = re.sub(r"\b(Per node type stats.*?)\b\btable", r"\1table2", html)
        html = re.sub(r"\b(Per node type stats.*?)\b\btable\>", r"\1table2>", html)

        soup = bs(html, 'lxml')
        rows = soup.find('table2').find_all('tr')

        with open(out_file, "w") as f:
            for r in rows[1:]:
                cols = r.find_all('td')
                line = '|'.join(c.text.strip() for c in cols)
                f.write(line + '\n')

    except Exception as e:
        print(f"⚠️  Parsing failed for Q{qid}: {e}")
        maxylist.append(0)
        maxnamelist.append("parse_failed")
        continue

    # Step 2: Read parsed stats and update graph data
    try:
        xlist.append(str(qid))
        with open(out_file, "r") as f:
            max_pct = 0
            max_func = "Other"
            for line in f:
                parts = line.strip().split("|")
                if len(parts) != 4: continue
                op, self_time, total_time, percent = parts
                pct_val = float(percent.replace("%", "").strip())
                if pct_val > max_pct:
                    max_pct = pct_val
                    max_func = op

                if op in functions:
                    ylist[functions.index(op)][qid-1] = pct_val
                else:
                    ylist[functions.index("Other")][qid-1] += pct_val

            maxnamelist.append(max_func)
            maxylist.append(max_pct)

    except Exception as e:
        print(f"⚠️  Error reading plan table for Q{qid}: {e}")
        maxnamelist.append("read_error")
        maxylist.append(0)

# === Normalize if needed
for i in range(99):
    total = sum(ylist[j][i] for j in range(len(functions)))
    if total > 100:
        for j in range(len(functions)):
            ylist[j][i] = (ylist[j][i] / total) * 100

# === Plot
plt.rcParams["font.size"] = 18
plt.figure(figsize=(32, 18))

bars1 = plt.bar(xlist, ylist[0], color=colors[0])
cum_sum = np.array(ylist[0])
for i in range(1, len(functions)):
    plt.bar(xlist, ylist[i], color=colors[i], bottom=cum_sum)
    cum_sum += np.array(ylist[i])

# Add % text above bars
for idx, bar in enumerate(bars1):
    plt.text(bar.get_x() + bar.get_width()/2, 110, f"%{maxylist[idx]:.1f}", ha='center', va='center', fontsize=16, rotation='vertical')

plt.title(TITLE, fontsize=28)
plt.xlabel("Query ID", fontsize=24)
plt.ylabel("Time Contribution (%)", fontsize=24)
plt.xticks(rotation=75)
plt.grid(True)

# Legend
patches = [mpatches.Patch(color=colors[i], label=functions[i]) for i in range(len(functions))]
plt.legend(handles=patches, loc="upper left", bbox_to_anchor=(1, 1), fontsize=18)

plt.tight_layout()
plt.savefig(f"/proj/{CHART_BASE_NAME}.pdf")
plt.savefig(f"/proj/{CHART_BASE_NAME}.png")
print("✅ Chart saved as PDF/PNG in /proj/")
