import json
import os
import random

SEED = 42
SIZES = [250, 500, 1000, 2000, 4000, 8000]
DENSE_SIZES = [125, 250, 500, 1000, 2000, 4000]
W_MAX = 100
OUT_DIR = "inputs"


def rng_for(case, n):
    return random.Random(f"{SEED}-{case}-{n}")


def random_graph(rng, n, m):
    edges = [(rng.randrange(v), v, rng.randint(1, W_MAX)) for v in range(1, n)]
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.append((u, v, rng.randint(1, W_MAX)))
    rng.shuffle(edges)
    return edges


def random_sparse(rng, n):
    return random_graph(rng, n, 4 * n)


def random_dense(rng, n):
    return random_graph(rng, n, n * n // 20)


def bf_best(rng, n):
    edges = [(i, i + 1, rng.randint(1, W_MAX)) for i in range(n - 1)]
    while len(edges) < 4 * n:
        u = rng.randrange(n - 1)
        edges.append((u, rng.randint(u + 1, n - 1), rng.randint(1, W_MAX)))
    edges.sort(key=lambda e: (e[0], e[1]))
    return edges


def bf_worst(rng, n):
    edges = [(i, i + 1, rng.randint(1, W_MAX)) for i in range(n - 1)]
    edges.reverse()
    return edges


def dij_worst(rng, n):
    t = n - 1
    edges = [(0, t, 3 * n)]
    for i in range(1, n - 1):
        edges.append((0, i, i))
        edges.append((i, t, 2 * n - 2 * i))
    return edges


CASES = {
    "random_sparse": (SIZES, random_sparse),
    "random_dense": (DENSE_SIZES, random_dense),
    "bf_best": (SIZES, bf_best),
    "bf_worst": (SIZES, bf_worst),
    "dij_worst": (SIZES, dij_worst),
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = []
    for case, (sizes, builder) in CASES.items():
        for n in sizes:
            edges = builder(rng_for(case, n), n)
            name = f"{case}_{n}.txt"
            with open(os.path.join(OUT_DIR, name), "w") as f:
                f.write(f"{n} {len(edges)} 0\n")
                f.writelines(f"{u} {v} {w}\n" for u, v, w in edges)
            manifest.append({"file": name, "case": case, "n": n, "m": len(edges), "src": 0})
            print(f"{name}: n={n} m={len(edges)}")
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)


if __name__ == "__main__":
    main()