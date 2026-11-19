# -*- coding: utf-8 -*-
"""
第22章 —— 22.4 拓扑排序 + 22.5 强连通分量
《算法导论（原书第3版）》CLRS ch22

TOPOLOGICAL-SORT：DFS 完成时间倒序。DAG 才存在。
Kosaraju SCC：两遍 DFS——①原图按完成时间倒序 ②转置图按该序再跑。
定理 22.16：分量图（condensation）是 DAG。

对拍：
  · 拓扑序 vs Kahn（入度剥离）算法
  · SCC vs 暴力传递闭包法（floyd-warshall 求 mutually reachable）
应用场景：课程先修依赖。
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch22_01_bfs_dfs import Graph


# ============================================================
# 22.4 拓扑排序
# ============================================================
def topological_sort(g):
    """DFS 完成时间倒序。O(V+E)。非 DAG 返回 None。"""
    d, f, par = g.dfs()
    # 有环检测：back edge 存在
    for (u, v) in g.edges:
        if d[v] <= d[u] < f[u] <= f[v]:
            return None
    return sorted(range(g.V), key=lambda x: -f[x])


def topological_sort_kahn(g):
    """Kahn 算法（练习 22.4-2）：入度表 + 队列剥离。对拍参照。"""
    indeg = [0] * g.V
    for u in range(g.V):
        for v in g.adj[u]:
            indeg[v] += 1
    from collections import deque
    q = deque([u for u in range(g.V) if indeg[u] == 0])
    out = []
    while q:
        u = q.popleft()
        out.append(u)
        for v in g.adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(out) != g.V:
        return None                    # 有环
    return out


def verify_topo(g, order):
    """校验：拓扑序中每条边 u→v 都 u 在 v 前。"""
    pos = {u: i for i, u in enumerate(order)}
    return all(pos[u] < pos[v] for (u, v) in g.edges)


def demo_topo_courses():
    print("=" * 60)
    print("22.4 拓扑排序（教科书穿衣问题，图 22.7）")
    # 一个图即可：watch(4) 无依赖不需边
    g = Graph(9, directed=True)
    label = ["袜子 socks", "内裤 undershorts", "裤子 pants", "鞋 shoes",
             "手表 watch", "腰带 belt", "衬衫 shirt", "领带 tie", "外套 jacket"]
    for u, v in [(0,2),(1,2),(1,3),(2,3),(2,5),(5,8),(6,7),(7,8)]:
        g.add_edge(u, v)
    ts = topological_sort(g)
    tk = topological_sort_kahn(g)
    ok1 = ts is not None and verify_topo(g, ts)
    ok2 = tk is not None and verify_topo(g, tk)
    print("  DFS 版:", [label[i] for i in ts])
    print("  Kahn 版:", [label[i] for i in tk])
    print(f"  两版均是合法拓扑序: DFS版 {'✓' if ok1 else '✗'} | Kahn版 {'✓' if ok2 else '✗'}")
    # 加环测试
    g.add_edge(8, 0)                       # jacket → socks 造环
    print("  加边 jacket→socks 造环后:", topological_sort(g), "(None = 正确拒绝)")
    # 随机 DAG fuzz：100 组
    random.seed(9)
    bad = 0
    for _ in range(100):
        V = random.randrange(6, 30)
        dag = Graph(V, directed=True)
        for u in range(V):
            # 只加 u→v (v>u) 的边保证无环
            for v in random.sample(range(u + 1, V), min(V - u - 1, random.randrange(0, 4))):
                dag.add_edge(u, v)
        got = topological_sort(dag)
        ref = topological_sort_kahn(dag)
        if got is None or not verify_topo(dag, got) or ref is None:
            bad += 1
    print(f"  100 组随机 DAG fuzz（序合法性校验）:", "✓" if bad == 0 else f"✗ {bad} 组")


# ============================================================
# 22.5 Kosaraju SCC
# ============================================================
def transpose(g):
    """转置图：所有边反向。"""
    gt = Graph(g.V, directed=True)
    for (u, v) in g.edges:
        gt.add_edge(v, u)
    return gt


def kosaraju_scc(g):
    """两遍 DFS。返回 scc_id[]（同分量同号）与分量列表。O(V+E)"""
    _, f, _ = g.dfs()
    order = sorted(range(g.V), key=lambda x: -f[x])   # 完成时间倒序
    gt = transpose(g)
    # 第二遍：转置图上按 order 跑 DFS，每棵树 = 一个 SCC
    color = [0] * g.V            # 0 white,1 gray,2 black
    scc_id = [-1] * g.V
    comps = []
    cid = 0

    def visit(u, comp):
        color[u] = 1
        scc_id[u] = cid
        comp.append(u)
        for v in gt.adj[u]:
            if color[v] == 0:
                visit(v, comp)
        color[u] = 2

    for s in order:
        if color[s] == 0:
            comp = []
            visit(s, comp)
            comps.append(comp)
            cid += 1
    return scc_id, comps


def scc_by_closure(g):
    """暴力参照：传递闭包法。u,v 同分量 ⇔ u→v 且 v→u（含 u==v）。O(V³)"""
    n = g.V
    reach = [[False] * n for _ in range(n)]
    for u in range(n):
        reach[u][u] = True
    for u in range(n):
        for v in g.adj[u]:
            reach[u][v] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                ri = reach[i]
                rk = reach[k]
                for j in range(n):
                    if rk[j]:
                        ri[j] = True
    scc_id = [-1] * n
    comps = []
    for u in range(n):
        if scc_id[u] == -1:
            comp = [v for v in range(n) if reach[u][v] and reach[v][u]]
            cid = len(comps)
            for v in comp:
                scc_id[v] = cid
            comps.append(comp)
    return scc_id, comps


def same_partition(s1, s2, n):
    """两个划分是否等价（不看编号，看分组）。"""
    for u in range(n):
        for v in range(n):
            if (s1[u] == s1[v]) != (s2[u] == s2[v]):
                return False
    return True


def demo_scc():
    print("=" * 60)
    print("22.5 Kosaraju 强连通分量")
    # 教科书图 22.9 同款（8 顶点）
    g = Graph(8, directed=True)
    for u, v in [(0,1),(1,2),(2,3),(3,2),(4,0),(1,4),(2,0),(5,6),(6,7),(7,5),(4,7)]:
        g.add_edge(u, v)
    scc_id, comps = kosaraju_scc(g)
    r_id, r_comps = scc_by_closure(g)
    print("  Kosaraju 分量:", sorted(sorted(c) for c in comps))
    print("  传递闭包参照:", sorted(sorted(c) for c in r_comps))
    print("  两法划分等价:", "✓" if same_partition(scc_id, r_id, g.V) else "✗")
    # 随机 fuzz
    random.seed(4)
    bad = 0
    for _ in range(60):
        V = random.randrange(5, 18)
        rg = Graph(V, directed=True)
        for u in range(V):
            for v in range(V):
                if u != v and random.random() < 0.22:
                    rg.add_edge(u, v)
        s1, _ = kosaraju_scc(rg)
        s2, _ = scc_by_closure(rg)
        if not same_partition(s1, s2, V):
            bad += 1
    print(f"  60 组随机有向图 fuzz:", "✓" if bad == 0 else f"✗ {bad} 组")


def main():
    demo_topo_courses()
    demo_scc()


if __name__ == "__main__":
    main()
