import time
import sys
from pathlib import Path


def get_int_val(cgroup_suffix: str) -> int:
    val = 0.0
    with open(f"/sys/fs/cgroup/{cgroup_suffix}", "r") as f:
        val = f.read()
    val = int(val)
    return val



def cpu_details(sleep_interval_ms = 1000) -> float:
    t1 = time.time_ns()
    c1 = get_int_val("/cpu/cpuacct.usage")

    time.sleep(sleep_interval_ms/1000)

    t2 = time.time_ns()
    c2 = get_int_val("/cpu/cpuacct.usage")

    if t2-t1 == 0:
        return 0.0

    return (c2-c1)*100/(float)(t2-t1)


def get_memory_usage():
    return get_int_val("memory/memory.usage_in_bytes") / (float)(1024.0*1024.0)


if __name__ == "__main__":
    print("ARGS: ", sys.argv)
    if len(sys.argv) < 2:
        print("Incorrect usage.\npython ./metric.py <file_to_write> <interval>.\nInterval is optional and defaults to 1s.")
        exit(1)

    file_to_write = Path(sys.argv[1])
    interval_ms = 1000

    if len(sys.argv) >= 3:
        interval_ms = int(sys.argv[2])

    print(f"writing to: {file_to_write} and interval_ms: {interval_ms}")
    if file_to_write.exists():
        file_to_write.unlink()


    while True:
        cpu_perc = cpu_details(interval_ms)
        memory_mb = get_memory_usage()
        line = f"{time.time_ns()} {cpu_perc}% {memory_mb}MB\n"
        print(f"Writing line: {line}")

        with open(file_to_write, "a") as f:
            f.write(line)
