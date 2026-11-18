import heapq

INF = float("inf")


def dijkstra(n, adj, src):
    """adj[u] = lista de (v, peso). Pesos >= 0. O((V+E) log V)."""
    dist = [INF] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist


def bellman_ford(n, edges, src):
    """edges = lista de (u, v, peso). O(V*E), com parada antecipada."""
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    return dist


def to_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


if __name__ == "__main__":
    import random

    random.seed(42)
    for _ in range(200):
        n = random.randint(1, 30)
        m = random.randint(0, 100)
        edges = [(random.randrange(n), random.randrange(n), random.randint(0, 20)) for _ in range(m)]
        assert dijkstra(n, to_adj(n, edges), 0) == bellman_ford(n, edges, 0)
    print("OK: Dijkstra == Bellman-Ford em 200 grafos aleatórios")
