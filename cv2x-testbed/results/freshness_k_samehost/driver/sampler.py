"""Sample /proc/loadavg and foreign CPU (all busy CPU minus this replicate's node + experiment) every 2 s."""
import os
import sys
import time

out = sys.argv[1]
OWN = ('--port 8562', 'experiment_freshness_k.py')
HZ = os.sysconf('SC_CLK_TCK')


def total_busy():
    with open('/proc/stat') as f:
        p = f.readline().split()[1:]
    v = list(map(int, p))
    idle = v[3] + v[4]
    return sum(v[:8]) - idle


def steal():
    return int(open('/proc/stat').readline().split()[8])


def own_jiffies():
    s = 0
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f'/proc/{pid}/cmdline', 'rb').read().replace(b'\0', b' ').decode(errors='ignore')
            if any(o in cmd for o in OWN) and 'sampler.py' not in cmd:
                st = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()
                s += int(st[11]) + int(st[12])
        except Exception:
            pass
    return s


tb0, ow0, t0, st0 = total_busy(), own_jiffies(), time.time(), steal()
while True:
    time.sleep(2)
    tb1, ow1, t1, st1 = total_busy(), own_jiffies(), time.time(), steal()
    dt = t1 - t0
    foreign = max(0.0, ((tb1 - tb0) - (ow1 - ow0)) / HZ / dt)
    own = (ow1 - ow0) / HZ / dt
    la = open('/proc/loadavg').read().strip()
    with open(out, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {la} foreign_cpu={foreign:.2f} own_cpu={own:.2f} steal_cpu={(st1 - st0) / HZ / dt:.3f}\n")
    tb0, ow0, t0, st0 = tb1, ow1, t1, st1
