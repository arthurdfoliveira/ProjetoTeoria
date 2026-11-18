import argparse
import csv
import gc
import json
import os
import statistics
import time

from caminho_minimo import bellman_ford, dijkstra, to_adj


def load(path):
    with open(path) as f:
        n, m, src = map(int, f.readline().split())
        edges = [tuple(map(int, line.split())) for line in f if line.strip()]
    return n, edges, src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--max-n", type=int, default=0, help="0 = sem limite")
    ap.add_argument("--manifest", default="inputs/manifest.json")
    ap.add_argument("--out", default="results/results_python.csv")
    args = ap.parse_args()

    base = os.path.dirname(args.manifest)
    with open(args.manifest) as f:
        manifest = json.load(f)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with open(args.out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["lang", "algo", "case", "n", "m", "reps", "mean_s", "std_s", "min_s"])
        for e in manifest:
            if args.max_n and e["n"] > args.max_n:
                continue
            n, edges, src = load(os.path.join(base, e["file"]))
            adj = to_adj(n, edges)
            runs = {
                "dijkstra": lambda: dijkstra(n, adj, src),
                "bellman_ford": lambda: bellman_ford(n, edges, src),
            }
            for algo, fn in runs.items():
                for _ in range(args.warmup):
                    fn()
                times = []
                gc.collect()
                gc.disable()
                for _ in range(args.reps):
                    t0 = time.perf_counter()
                    fn()
                    times.append(time.perf_counter() - t0)
                gc.enable()
                mean = statistics.mean(times)
                std = statistics.stdev(times) if len(times) > 1 else 0.0
                w.writerow(["python", algo, e["case"], e["n"], e["m"], args.reps,
                            f"{mean:.9f}", f"{std:.9f}", f"{min(times):.9f}"])
                fo.flush()
                print(f"python {algo:13s} {e['case']:14s} n={e['n']:5d} m={e['m']:7d} "
                      f"mean={mean * 1000:10.3f} ms  std={std * 1000:9.3f} ms", flush=True)


if __name__ == "__main__":
    main()