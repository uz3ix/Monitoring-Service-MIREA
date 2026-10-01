from collector import (
    get_cpu_percent, 
    get_memory_usage, 
    get_disk_usage,
    collect_metrics
)

import psutil

print(get_cpu_percent())
print(get_memory_usage())
# print(get_disk_usage(["C:/"]))

print("///////////")

# print(collect_metrics("C:/"))


print(psutil.disk_partitions(all=False))



import json
from collector import (
    get_disks_usage
)

print(json.dumps(get_disks_usage(), indent=4, ensure_ascii=False))

print(get_disk_usage("C:/"))