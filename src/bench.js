const fs = require("fs");
const path = require("path");
const { dijkstra, bellmanFord, toAdj, checksum } = require("./caminho_minimo.js");

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : def;
};
const reps = parseInt(opt("--reps", "15"));
const warmup = parseInt(opt("--warmup", "5"));
const maxN = parseInt(opt("--max-n", "0"));
const manifestPath = opt("--manifest", "inputs/manifest.json");
const outPath = opt("--out", "results/results_js.csv");
const checkMode = args.includes("--check");

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

if (checkMode) {
  const out = {};
  for (const e of manifest) {
    if (maxN && e.n > maxN) continue;
    const { n, edges, src } = load(path.join(base, e.file));
    out[e.file] = {
      dijkstra: checksum(dijkstra(n, toAdj(n, edges), src)),
      bellman_ford: checksum(bellmanFord(n, edges, src)[0]),
    };
  }
  console.log(JSON.stringify(out));
  process.exit(0);
}

fs.mkdirSync(path.dirname(outPath), { recursive: true });
const rows = ["lang,algo,case,n,m,reps,mean_s,std_s,min_s"];
const now = () => Number(process.hrtime.bigint()) / 1e9;

for (const e of manifest) {
  if (maxN && e.n > maxN) continue;
  const { n, edges, src } = load(path.join(base, e.file));
  const adj = toAdj(n, edges);
  const runs = {
    dijkstra: () => dijkstra(n, adj, src),
    bellman_ford: () => bellmanFord(n, edges, src),
  };
  for (const [algo, fn] of Object.entries(runs)) {
    for (let i = 0; i < warmup; i++) fn();
    const times = [];
    for (let i = 0; i < reps; i++) {
      const t0 = now();
      fn();
      times.push(now() - t0);
    }
    const mean = times.reduce((a, b) => a + b, 0) / times.length;
    const std = times.length > 1
      ? Math.sqrt(times.reduce((a, t) => a + (t - mean) ** 2, 0) / (times.length - 1))
      : 0;
    rows.push(["js", algo, e.case, e.n, e.m, reps, mean.toFixed(9), std.toFixed(9), Math.min(...times).toFixed(9)].join(","));
    fs.writeFileSync(outPath, rows.join("\n") + "\n");
    console.log(`js     ${algo.padEnd(13)} ${e.case.padEnd(14)} n=${String(e.n).padStart(5)} m=${String(e.m).padStart(7)} ` +
      `mean=${(mean * 1000).toFixed(3).padStart(10)} ms  std=${(std * 1000).toFixed(3).padStart(9)} ms`);
  }
}