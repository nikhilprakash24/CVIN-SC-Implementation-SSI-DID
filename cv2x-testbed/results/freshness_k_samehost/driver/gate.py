"""Wait (max 900 s) until total busy CPU over a 5 s window is < 0.7 CPUs (no replicate running yet, so all is foreign)."""
import time


def busy():
    v = list(map(int, open('/proc/stat').readline().split()[1:9]))
    return sum(v) - v[3] - v[4]


t_start = time.time()
while True:
    b0 = busy()
    time.sleep(5)
    cpu = (busy() - b0) / 100 / 5
    if cpu < 0.7 or time.time() - t_start > 900:
        print(f"gate: waited {time.time() - t_start:.0f} s; busy CPUs over last 5 s = {cpu:.2f}; "
              f"loadavg {open('/proc/loadavg').read().strip()}")
        break
