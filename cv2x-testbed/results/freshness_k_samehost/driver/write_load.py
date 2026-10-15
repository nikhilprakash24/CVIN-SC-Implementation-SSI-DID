import json
import sys

out, rep, mode, ord_, t0, l0, t1, l1, samp, rc = sys.argv[1:]
samples = []
for line in open(samp):
    p = line.split()
    kv = dict(x.split('=') for x in p[6:])
    samples.append({'t': p[0], 'loadavg': ' '.join(p[1:6]), 'load1': float(p[1]),
                    'foreign_cpu': float(kv['foreign_cpu']), 'own_cpu': float(kv['own_cpu']),
                    'steal_cpu': float(kv['steal_cpu']) if 'steal_cpu' in kv else None})
d = {'replicate': int(rep), 'mode': mode, 'order_index': int(ord_),
     'node': 'fresh hardhat node :8562 (block 0) started for this replicate, killed by PID (process group)',
     'start_utc': t0, 'loadavg_start': l0, 'load1_start': float(l0.split()[0]),
     'end_utc': t1, 'loadavg_end': l1, 'load1_end': float(l1.split()[0]),
     'sample_interval_s': 2,
     'foreign_cpu_definition': 'CPUs busy outside this replicate (all busy jiffies minus the hardhat node on :8562 and experiment_freshness_k.py), per 2 s sample',
     'foreign_cpu_mean': sum(s['foreign_cpu'] for s in samples) / len(samples) if samples else None,
     'foreign_cpu_max': max(s['foreign_cpu'] for s in samples) if samples else None,
     'own_cpu_mean': sum(s['own_cpu'] for s in samples) / len(samples) if samples else None,
     'steal_cpu_mean': (sum(s['steal_cpu'] for s in samples) / len(samples)
                        if samples and all(s['steal_cpu'] is not None for s in samples) else None),
     'load1_max_sampled': max(s['load1'] for s in samples) if samples else None,
     'load1_mean_sampled': sum(s['load1'] for s in samples) / len(samples) if samples else None,
     'n_samples': len(samples), 'exit_code': int(rc), 'samples': samples}
with open(out, 'w') as f:
    json.dump(d, f, indent=1)
print({k: v for k, v in d.items() if k != 'samples'})
