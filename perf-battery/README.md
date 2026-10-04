# Performance Battery

Throughput (iperf3 up/down) and HTTP latency (p50/mean/max over 50
samples per rep) through the access path under test, 5 repetitions,
one CSV row per measurement so dispersion is computable.

```bash
# on the target (tpi2-3 or AWS app): iperf3 -s
# on the emulated remote worker, through the path under test:
./run_perf.py --phase phase-1 --path vpn \
    --iperf-server 10.0.0.73 --http-url http://10.0.0.73:8080/
```

Protocol (methodology: performance-variability mitigation):

- Same probing machine, network, and time-of-day discipline across paths.
- `--path baseline` = direct LAN run first, to separate substrate cost
  from access-path cost.
- Repeat per path: `vpn`, `openziti`, `netbird`.
- Failed reps record NaN with detail rather than being dropped.
- Commit `results/*.csv`; report mean and standard deviation.
