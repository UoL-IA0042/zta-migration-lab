# Performance Battery

Throughput (iperf3 up/down) and HTTP latency (p50/mean/max over 50
samples per rep) through the access path under test, 5 repetitions,
one CSV row per measurement so dispersion is computable.

```bash
# target: tpi2-3 runs lab-iperf3.service (deployed by ansible-workloads, :5201).
# The AWS app has no internet route, so the AWS path is HTTP latency only.
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

Phase 2, OpenZiti (logged in as `remote-admin`, the only role that may
dial `perf-iperf3`; same Mac, hotspot and protocol as Phase 1, including
the control ping before each run). The Phase 1 baseline is not repeated:
the substrate is unchanged.

```bash
./run_perf.py --phase phase-2-openziti --path openziti \
    --iperf-server 10.0.0.73 --http-url http://10.0.0.73:8080/
./run_perf.py --phase phase-2-openziti --path openziti-aws \
    --http-url http://10.100.10.10:8080/
```

Phase 2, NetBird (profile `remote-admin`, same protocol). Record the
connection type to tpi2-4 and nb-edge before each path (`netbird status
-d`): P2P and relayed runs are different paths and are reported apart.

```bash
./run_perf.py --phase phase-2-netbird --path netbird \
    --iperf-server 10.0.0.73 --http-url http://10.0.0.73:8080/
./run_perf.py --phase phase-2-netbird --path netbird-aws \
    --http-url http://10.100.10.10:8080/
```

Path note for the analysis: `vpn` carried client traffic Mac -> tpi2-4
(home, over the ISP gateway); `openziti` carries it Mac -> public router
(AWS) -> link -> tpi2-4, and `openziti-aws` Mac -> public router ->
aws-app inside the VPC (no site-to-site hop). The routes differ, not
only the access technology.
