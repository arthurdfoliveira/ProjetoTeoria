import argparse
import csv
import gc
import json
import os
import tracemalloc

from caminho_minimo import bellman_ford, dijkstra, to_adj


def load(path):
    with open(path) as f:
        n, m, src = map(int, f.readline().split())
        edges = [tuple(map(int, line.split())) for line in f if line.strip()]
    return n, edges, src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=0)
    ap.add_argument("--manifest", default="inputs/manifest.json")
    ap.add_argument("--out", default="results/results_mem_python.csv")
    args = ap.parse_args()

    base = os.path.dirname(args.manifest)
    manifest = json.load(open(args.manifest))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with open(args.out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["lang", "algo", "case", "n", "m", "peak_bytes"])
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
                gc.collect()
                tracemalloc.start()
                tracemalloc.reset_peak()
                before = tracemalloc.get_traced_memory()[0]
                result = fn()
                peak = tracemalloc.get_traced_memory()[1] - before
                tracemalloc.stop()
                del result
                w.writerow(["python", algo, e["case"], e["n"], e["m"], peak])
                fo.flush()
                print(f"python {algo:13s} {e['case']:14s} n={e['n']:5d} m={e['m']:7d} pico={peak / 1024:10.1f} KiB", flush=True)


if __name__ == "__main__":
    main()