const INF = Infinity;

// Min-heap binário de pares [dist, vértice]
class MinHeap {
  constructor() { this.a = []; }
  get size() { return this.a.length; }
  push(x) {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (a[p][0] <= a[i][0]) break;
      [a[p], a[i]] = [a[i], a[p]];
      i = p;
    }
  }
  pop() {
    const a = this.a;
    const top = a[0];
    const last = a.pop();
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {
        let l = 2 * i + 1, r = l + 1, m = i;
        if (l < a.length && a[l][0] < a[m][0]) m = l;
        if (r < a.length && a[r][0] < a[m][0]) m = r;
        if (m === i) break;
        [a[m], a[i]] = [a[i], a[m]];
        i = m;
      }
    }
    return top;
  }
}

// adj[u] = lista de [v, peso]. Pesos >= 0. O((V+E) log V)
function dijkstra(n, adj, src) {
  const dist = new Array(n).fill(INF);
  dist[src] = 0;
  const heap = new MinHeap();
  heap.push([0, src]);
  while (heap.size) {
    const [d, u] = heap.pop();
    if (d > dist[u]) continue;
    for (const [v, w] of adj[u]) {
      const nd = d + w;
      if (nd < dist[v]) {
        dist[v] = nd;
        heap.push([nd, v]);
      }
    }
  }
  return dist;
}

// edges = lista de [u, v, peso]. O(V*E), com parada antecipada
function bellmanFord(n, edges, src) {
  const dist = new Array(n).fill(INF);
  dist[src] = 0;
  for (let i = 0; i < n - 1; i++) {
    let changed = false;
    for (const [u, v, w] of edges) {
      if (dist[u] !== INF && dist[u] + w < dist[v]) {
        dist[v] = dist[u] + w;
        changed = true;
      }
    }
    if (!changed) break;
  }
  return dist;
}

function toAdj(n, edges) {
  const adj = Array.from({ length: n }, () => []);
  for (const [u, v, w] of edges) adj[u].push([v, w]);
  return adj;
}

module.exports = { dijkstra, bellmanFord, toAdj };

if (require.main === module) {
  const assert = require("assert");
  for (let t = 0; t < 200; t++) {
    const n = 1 + Math.floor(Math.random() * 30);
    const m = Math.floor(Math.random() * 100);
    const edges = Array.from({ length: m }, () => [
      Math.floor(Math.random() * n),
      Math.floor(Math.random() * n),
      Math.floor(Math.random() * 21),
    ]);
    assert.deepStrictEqual(dijkstra(n, toAdj(n, edges), 0), bellmanFord(n, edges, 0));
  }
  console.log("OK: Dijkstra == Bellman-Ford em 200 grafos aleatórios");
}
