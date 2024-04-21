import json
from collections import defaultdict
import sys
import numpy as np

import sqlite3
import json
from datetime import datetime

data = None
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

dbname = f'perfdata-{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}.db' if len(sys.argv) <= 2 else sys.argv[2]

conn = sqlite3.connect(dbname)
conn.execute(
    "CREATE TABLE regions (region_id int not null, name text not null, parent_id int, real_time int, cycles int);")
regions = data["threads"]["0"]["regions"]

for region_id in regions:
    region = regions[region_id]
    conn.execute("INSERT INTO regions (region_id, name, parent_id, real_time, cycles) VALUES (?, ?, ?, ?, ?)",
                 (int(region_id), region["name"], int(region["parent_region_id"]), int(region["real_time_nsec"]),
                  int(region["cycles"])))
conn.commit()