import json
import os
import subprocess
import sys

from caminho_minimo import INF, bellman_ford, checksum, dijkstra, to_adj


def load(path):
    with open(path) as f:
        n, m, src = map(int, f.readline().split())
        edges = [tuple(map(int, line.split())) for line in f if line.strip()]
    return n, edges, src


def test_ciclo_negativo():
    d, neg = bellman_ford(3, [(0, 1, 4), (1, 2, -2), (0, 2, 5)], 0)
    assert d == [0, 4, 2] and not neg
    _, neg = bellman_ford(3, [(0, 1, 1), (1, 2, -3), (2, 1, 1)], 0)
    assert neg
    d, neg = bellman_ford(3, [(0, 1, 1)], 0)
    assert d == [0, 1, INF] and not neg
    code = ("const {bellmanFord}=require('./caminho_minimo.js');"
            "console.log(JSON.stringify([bellmanFord(3,[[0,1,4],[1,2,-2],[0,2,5]],0)[1],"
            "bellmanFord(3,[[0,1,1],[1,2,-3],[2,1,1]],0)[1]]))")
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [False, True]
    print("OK: deteccao de ciclo negativo (Python e JS)")


def test_mesmas_entradas(max_n):
    manifest = json.load(open("inputs/manifest.json"))
    cmd = ["node", "bench.js", "--check"] + (["--max-n", str(max_n)] if max_n else [])
    js = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    total = 0
    for e in manifest:
        if max_n and e["n"] > max_n:
            continue
        n, edges, src = load(os.path.join("inputs", e["file"]))
        py = {
            "dijkstra": checksum(dijkstra(n, to_adj(n, edges), src)),
            "bellman_ford": checksum(bellman_ford(n, edges, src)[0]),
        }
        got = {
            "py_dijkstra": py["dijkstra"], "py_bf": py["bellman_ford"],
            "js_dijkstra": js[e["file"]]["dijkstra"], "js_bf": js[e["file"]]["bellman_ford"],
        }
        assert len({json.dumps(v) for v in got.values()}) == 1, f"divergencia em {e['file']}: {got}"
        total += 1
    print(f"OK: 4 implementacoes concordam em {total} entradas")


if __name__ == "__main__":
    mx = int(sys.argv[sys.argv.index("--max-n") + 1]) if "--max-n" in sys.argv else 0
    if not os.path.exists("inputs/manifest.json"):
        sys.exit("Rode antes: python3 gen_inputs.py")
    test_ciclo_negativo()
    test_mesmas_entradas(mx)