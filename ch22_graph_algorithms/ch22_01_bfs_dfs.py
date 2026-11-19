# -*- coding: utf-8 -*-
"""
第22章 基本的图算法 —— 22.1 图的表示 + 22.2 BFS + 22.3 DFS
《算法导论（原书第3版）》CLRS ch22

BFS：无权图最短路径（边数最少）。O(V+E)
DFS：发现/完成时间戳、括号化定理、边四分类（树/前向/后向/交叉）。O(V+E)
"""

from collections import deque


class Graph:
    """邻接表图。0..V-1 编号，支持有向/无向。"""

    def __init__(self, V, directed=False):
        self.V = V
        self.directed = directed
        self.adj = [[] for _ in range(V)]
        self.edges = []

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.edges.append((u, v))
        if not self.directed:
            self.adj[v].append(u)

    # ---------------- 22.2 BFS ----------------
    def bfs(self, s):
        """返回 dist[]：s 到各点最少边数（不可达 = inf）。O(V+E)"""
        INF = float("inf")
        dist = [INF] * self.V
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                if dist[v] == INF:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    def bfs_path(self, s, t):
        """最短路径本身（任一条）。"""
        if s == t:
            return [s]
        INF = float("inf")
        dist = [INF] * self.V
        par = [None] * self.V
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                if dist[v] == INF:
                    dist[v] = dist[u] + 1
                    par[v] = u
                    if v == t:
                        path = [v]
                        while path[-1] != s:
                            path.append(par[path[-1]])
                        return path[::-1]
                    q.append(v)
        return None

    # ---------------- 22.3 DFS ----------------
    def dfs(self, order=None):
        """完整 DFS（森林）。返回 (d, f, parent)。
        order：主循环顶点序（拓扑/SCC 复用）。递归深度受 V 限制，演示规模安全。"""
        WHITE, GRAY, BLACK = 0, 1, 2
        self._color = [WHITE] * self.V
        d = [None] * self.V
        f = [None] * self.V
        parent = [None] * self.V
        self._t = 0

        def visit(u):
            self._t += 1
            d[u] = self._t
            self._color[u] = GRAY
            for v in self.adj[u]:
                if self._color[v] == WHITE:
                    parent[v] = u
                    visit(v)
            self._t += 1
            f[u] = self._t
            self._color[u] = BLACK

        for u in (order if order is not None else range(self.V)):
            if self._color[u] == WHITE:
                visit(u)
        return d, f, parent


def edge_classify(u, v, d, f, parent):
    """单条边 (u,v) 的四分类（定理 22.10 / 图 22.9）。"""
    if parent[v] == u:
        return "tree"
    if d[u] < d[v] < f[v] < f[u]:
        return "forward"
    if d[v] <= d[u] < f[u] <= f[v]:
        return "back"
    return "cross"


def brute_shortest_dist(g, s, t, maxd=None):
    """暴力逐层扩展（对拍参照）。不可达返回 None。"""
    if s == t:
        return 0
    cur = {s}
    seen = {s}
    for depth in range(1, (maxd or g.V)):
        nxt = set()
        for u in cur:
            for v in g.adj[u]:
                if v not in seen:
                    seen.add(v)
                    nxt.add(v)
        if t in nxt:
            return depth
        if not nxt:
            break
        cur = nxt
    return None


def demo_bfs():
    print("=" * 60)
    print("22.2 BFS 最短路径（无权图）")
    g = Graph(8, directed=False)
    for u, v in [(0,1),(0,4),(1,5),(2,5),(2,6),(2,3),(3,6),(3,7),(5,6),(6,7)]:
        g.add_edge(u, v)
    dist = g.bfs(0)
    print("  源 0 的 dist:", dist)
    path = g.bfs_path(0, 7)
    print("  0→7 最短路径:", path, "| 长度:", len(path) - 1)
    # 全源对拍：64 组（含不可达）
    bad = 0
    for s in range(g.V):
        ds = g.bfs(s)
        for t in range(g.V):
            bd = brute_shortest_dist(g, s, t)
            if bd is None:
                if ds[t] != float("inf"):
                    bad += 1
            elif ds[t] != bd:
                bad += 1
    print("  全源 8×8 距离 vs 暴力逐层对拍:", "✓" if bad == 0 else f"✗ {bad} 项")


def demo_dfs():
    print("=" * 60)
    print("22.3 DFS：时间戳 / 括号化定理 / 边分类")
    g = Graph(8, directed=True)
    for u, v in [(0,1),(1,2),(2,3),(3,2),(4,0),(1,4),(2,0),(5,6),(6,7),(7,5),(4,7)]:
        g.add_edge(u, v)
    d, f, par = g.dfs(order=[4,3,2,1,0,7,6,5])   # 教科书图 22.4 同款访问序
    print("  d:", d)
    print("  f:", f)
    ok_nest = True
    for u in range(g.V):
        for v in range(g.V):
            if u == v:
                continue
            # 区间 [d,f) 半交（一端在内一端在外）= 违反括号化
            half = (d[u] < d[v] < f[u] < f[v]) or (d[v] < d[u] < f[v] < f[u])
            if half:
                ok_nest = False
    print("  括号化定理（任意两区间要么嵌套要么不相交）:", "✓" if ok_nest else "✗")
    from collections import Counter
    cnt = Counter(edge_classify(u, v, d, f, par) for (u, v) in g.edges)
    print("  边分类:", dict(cnt))
    print("  后向边>0 ⇔ 图有环（本图有 2→3→2 与 5→6→7→5）:",
          "✓" if cnt["back"] > 0 else "✗")


def main():
    demo_bfs()
    demo_dfs()


if __name__ == "__main__":
    main()
