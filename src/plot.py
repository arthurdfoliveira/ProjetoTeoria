import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = "results"
FIGS = os.path.join(RES, "figs")
CASES = ["random_sparse", "random_dense", "bf_best", "bf_worst", "dij_worst"]
LABEL = {
    "random_sparse": "Aleatório esparso (E=4V)",
    "random_dense": "Aleatório denso (E=V²/20)",
    "bf_best": "Melhor caso Bellman-Ford",
    "bf_worst": "Pior caso Bellman-Ford",
    "dij_worst": "Pior caso Dijkstra (heap)",
}
COLOR = {"dijkstra": "tab:blue", "bellman_ford": "tab:red"}
STYLE = {"python": "-o", "js": "--s"}


def load():
    rows = []
    for lang in ("python", "js"):
        p = os.path.join(RES, f"results_{lang}.csv")
        if not os.path.exists(p):
            print("faltando", p)
            continue
        with open(p) as f:
            for r in csv.DictReader(f):
                rows.append({"lang": r["lang"], "algo": r["algo"], "case": r["case"], "n": int(r["n"]),
                             "m": int(r["m"]), "mean": float(r["mean_s"]), "std": float(r["std_s"])})
    return rows


def f_theory(algo, case, n, m):
    if algo == "dijkstra":
        return (n + m) * math.log2(n)
    if case == "bf_best":
        return m
    return n * m


def series(rows, algo, lang, case):
    pts = sorted((r for r in rows if r["algo"] == algo and r["lang"] == lang and r["case"] == case),
                 key=lambda r: r["n"])
    return pts


def grid(title_fn, draw, fname, ylabel):
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, case in zip(axes.flat, CASES):
        draw(ax, case)
        ax.set_title(LABEL[case])
        ax.set_xlabel("V (nº de vértices)")
        ax.set_ylabel(ylabel)
        ax.grid(True, which="both", alpha=0.3)
    axes.flat[-1].axis("off")
    h, l = axes.flat[0].get_legend_handles_labels()
    axes.flat[-1].legend(h, l, loc="center", fontsize=12)
    fig.suptitle(title_fn)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, fname), dpi=150)
    plt.close(fig)


def main():
    rows = load()
    if not rows:
        raise SystemExit("Sem resultados. Rode bench.py e bench.js antes.")
    os.makedirs(FIGS, exist_ok=True)

    def draw_time(ax, case):
        for algo in COLOR:
            for lang in STYLE:
                pts = series(rows, algo, lang, case)
                if pts:
                    ax.errorbar([p["n"] for p in pts], [p["mean"] for p in pts], yerr=[p["std"] for p in pts],
                                fmt=STYLE[lang], color=COLOR[algo], capsize=3, label=f"{algo} ({lang})")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
    grid("Tempo medido (média ± desvio-padrão), escala log-log", draw_time, "tempo_loglog.png", "tempo (s)")

    def draw_ratio(ax, case):
        for algo in COLOR:
            for lang in STYLE:
                pts = series(rows, algo, lang, case)
                if pts:
                    ax.plot([p["n"] for p in pts],
                            [p["mean"] / f_theory(algo, case, p["n"], p["m"]) for p in pts],
                            STYLE[lang], color=COLOR[algo], label=f"{algo} ({lang})")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
    grid("Razão T(n)/f(n) (constante = complexidade correta)", draw_ratio, "razao_T_sobre_f.png", "T(n)/f(n)")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, algo in zip(axes, COLOR):
        for case in CASES:
            py, js = series(rows, algo, "python", case), series(rows, algo, "js", case)
            js_by_n = {p["n"]: p["mean"] for p in js}
            pts = [(p["n"], p["mean"] / js_by_n[p["n"]]) for p in py if p["n"] in js_by_n]
            if pts:
                ax.plot(*zip(*pts), "-o", label=LABEL[case])
        ax.set_xscale("log", base=2)
        ax.set_title(algo)
        ax.set_xlabel("V")
        ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("tempo Python / tempo JS")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "python_vs_js.png"), dpi=150)
    plt.close(fig)

    idx = {(r["case"], r["n"], r["algo"], r["lang"]): r for r in rows}
    keys = sorted({(r["case"], r["n"], r["m"]) for r in rows}, key=lambda k: (CASES.index(k[0]), k[1]))
    with open(os.path.join(RES, "tabela.md"), "w") as f:
        f.write("| Caso | V | E | Dijkstra Py (ms) | Dijkstra JS (ms) | Bellman-Ford Py (ms) | Bellman-Ford JS (ms) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for case, n, m in keys:
            cells = []
            for algo in COLOR:
                for lang in ("python", "js"):
                    r = idx.get((case, n, algo, lang))
                    cells.append(f"{r['mean'] * 1000:.3f} ± {r['std'] * 1000:.3f}" if r else "-")
            f.write(f"| {LABEL[case]} | {n} | {m} | " + " | ".join(cells) + " |\n")
    plot_memory()
    print("Gráficos em", FIGS, "e tabela em results/tabela.md")


def plot_memory():
    mem = []
    for lang in ("python",):
        p = os.path.join(RES, f"results_mem_{lang}.csv")
        if os.path.exists(p):
            with open(p) as f:
                for r in csv.DictReader(f):
                    mem.append({"lang": r["lang"], "algo": r["algo"], "case": r["case"],
                                "n": int(r["n"]), "m": int(r["m"]), "peak": float(r["peak_bytes"])})
    if not mem:
        return
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, case in zip(axes.flat, CASES):
        ref = None
        for algo in COLOR:
            for lang in STYLE:
                pts = series(mem, algo, lang, case)
                if pts:
                    ax.plot([p["n"] for p in pts], [max(p["peak"], 1) for p in pts], STYLE[lang],
                            color=COLOR[algo], label=f"{algo} ({lang})")
                    if ref is None and lang == "python":
                        ref = pts
        if ref:
            d0 = series(mem, "dijkstra", "python", case)[0]
            ns = [p["n"] for p in ref]
            ax.plot(ns, [d0["peak"] * (p["n"] + p["m"]) / (d0["n"] + d0["m"]) for p in ref],
                    ":", color="gray", label="∝ V+E")
            ax.plot(ns, [d0["peak"] * p["n"] / d0["n"] for p in ref], ":", color="black", label="∝ V")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_title(LABEL[case])
        ax.set_xlabel("V (nº de vértices)")
        ax.set_ylabel("memória extra (bytes)")
        ax.grid(True, which="both", alpha=0.3)
    axes.flat[-1].axis("off")
    h, l = axes.flat[0].get_legend_handles_labels()
    axes.flat[-1].legend(h, l, loc="center", fontsize=12)
    fig.suptitle("Memória extra do algoritmo em Python (pico via tracemalloc) × complexidade de espaço")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "memoria.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()