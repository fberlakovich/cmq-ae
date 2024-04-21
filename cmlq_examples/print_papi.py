import json
from collections import defaultdict
import sys
import numpy as np

import sqlite3
import json
from datetime import datetime

import functools

conn = sqlite3.connect(sys.argv[1])


def calculate_data(region_data):
    count = len(region_data)
    assert count > 0

    time_median = np.median([int(region["real_time_nsec"]) for region in region_data])
    cycles_median = np.median([int(region["cycles"]) for region in region_data])

    return time_median, cycles_median, count


indexed = defaultdict(list)

children = defaultdict(lambda: defaultdict(list))
region_names = ("add_f_f_iterator_loop", "cmlq_adouble_add_adouble_iterator_loop")

for region in region_names:
    cursor = conn.execute("SELECT * FROM regions WHERE name = ?", (region,))
    region_id = None
    for data in cursor:
        region_id = data[0]
        indexed[region].append({"cycles": data[4], "real_time_nsec": data[3]})

    cursor = conn.execute("SELECT * FROM regions WHERE parent_id = ?", (region_id,))
    for data in cursor:
        children[region][data[1]].append({"cycles": data[4], "real_time_nsec": data[3]})

baseline, other = region_names


def print_data(baseline, other, data_baseline, data_other):
    time_baseline, cycles_baseline, count_baseline = calculate_data(data_baseline[baseline])
    time_other, cycles_other, count_other = calculate_data(data_other[other])
    print(f"{baseline} ({count_baseline}): {time_baseline} ns, {cycles_baseline} cycles")
    print(f"{other} ({count_other}): {time_other} ns, {cycles_other} cycles")
    print(f"Difference: {time_baseline / time_other:.2f}x time, {cycles_baseline / cycles_other:.2f}x cycles")
    print()


print_data(baseline, other, indexed, indexed)
print("Children:")
for child_region in children[baseline]:
    print_data(child_region, child_region, children[baseline], children[other])


