const fs = require("fs");
const path = require("path");
const { dijkstra, bellmanFord, toAdj } = require("./caminho_minimo.js");

if (typeof global.gc !== "function") {
  console.error("Rode com: node --expose-gc --min-semi-space-size=256 --max-semi-space-size=256 bench_mem.js");
  process.exit(1);
}

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : def;
};
const maxN = parseInt(opt("--max-n", "0"));
const manifestPath = opt("--manifest", "inputs/manifest.json");
const outPath = opt("--out", "results/results_mem_js.csv");

function load(file) {
  const lines = fs.readFileSync(file, "utf8").split("\n");
  const [n, , src] = lines[0].split(" ").map(Number);
  const edges = [];
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].length) edges.push(lines[i].split(" ").map(Number));
  }
  return { n, edges, src };
}

const base = path.dirname(manifestPath);
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const rows = ["lang,algo,case,n,m,peak_bytes,retained_bytes"];

for (const e of manifest) {
  if (maxN && e.n > maxN) continue;
  const { n, edges, src } = load(path.join(base, e.file));
  const adj = toAdj(n, edges);
  const runs = {
    dijkstra: () => dijkstra(n, adj, src),
    bellman_ford: () => bellmanFord(n, edges, src),
  };
  for (const [algo, fn] of Object.entries(runs)) {
    fn();
    global.gc();
    const before = process.memoryUsage().heapUsed;
    const result = fn();
    const used = Math.max(0, process.memoryUsage().heapUsed - before);
    global.gc();
    const retained = Math.max(0, process.memoryUsage().heapUsed - before);
    rows.push(["js", algo, e.case, e.n, e.m, used, retained].join(","));
    fs.writeFileSync(outPath, rows.join("\n") + "\n");
    console.log(`js     ${algo.padEnd(13)} ${e.case.padEnd(14)} n=${String(e.n).padStart(5)} m=${String(e.m).padStart(7)} ` +
      `alocado=${(used / 1024).toFixed(1).padStart(10)} KiB  retido=${(retained / 1024).toFixed(1).padStart(8)} KiB`);
    void result;
  }
}