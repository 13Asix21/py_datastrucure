# -*- coding: utf-8 -*-
"""
第23章 最小生成树 —— 23.1~23.2 Kruskal + Prim
《算法导论（原书第3版）》CLRS ch23

MST 性质（定理 23.1）：切割安全边。
Kruskal：全边排序 + 并查集判环。O(E lg E)。
Prim：键值驱动，小顶堆 O(E lg V)；斐波那契堆 O(E + V lg V)。

对拍：两法互相校验 + 总权值一致 + 树性校验（连通无环）。
应用：电网/网络布线，权重量级对比（均匀 vs 大间距）。
"""

import os
import sys
import heapq
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch21_disjoint_sets"))
from ch21_disjoint_set import DisjointSetForest


def gen_connected_undirected(V, E, seed=7, max_w=10_000):
    """连通无向带权图：生成树骨架 + 随机边。返回 (adj, edges)。"""
    random.seed(seed)
    adj = [[] for _ in range(V)]                 # [(v, w)]
    edges = []                                   # (w, u, v)
    for v in range(1, V):
        u = random.randrange(v)
        w = random.randrange(1, max_w)
        adj[u].append((v, w))
        adj[v].append((u, w))
        edges.append((w, u, v))
    for _ in range(max(E - (V - 1), 0)):
        u, v = random.randrange(V), random.randrange(V)
        if u != v:
            w = random.randrange(1, max_w)
            adj[u].append((v, w))
            adj[v].append((u, w))
            edges.append((w, u, v))
    return adj, edges


# ============================================================
# 23.2 Kruskal
# ============================================================
def kruskal(V, edges):
    """Kruskal：边排序 + DSU。返回 (mst_edges, total)。O(E lg E)"""
    dsu = DisjointSetForest()
    nodes = [dsu.make_set(i) for i in range(V)]
    mst = []
    total = 0
    for w, u, v in sorted(edges):
        if dsu.find_set(nodes[u]) is not dsu.find_set(nodes[v]):
            dsu.union(nodes[u], nodes[v])
            mst.append((w, u, v))
            total += w
            if len(mst) == V - 1:
                break
    return mst, total


# ============================================================
# 23.2 Prim
# ============================================================
def prim(V, adj, start=0):
    """Prim + 小顶堆。返回 (mst_edges, total)。O(E lg V)"""
    INF = float("inf")
    key = [INF] * V
    in_tree = [False] * V
    parent = [None] * V
    key[start] = 0
    pq = [(0, start)]
    mst = []
    total = 0
    while pq:
        k, u = heapq.heappop(pq)
        if in_tree[u]:
            continue                              # 惰性删除
        in_tree[u] = True
        total += k
        if parent[u] is not None:
            mst.append((k, parent[u], u))
        for v, w in adj[u]:
            if not in_tree[v] and w < key[v]:
                key[v] = w
                parent[v] = u
                heapq.heappush(pq, (w, v))
    return mst, total


def is_spanning_tree(V, mst_edges):
    """校验：V-1 条边 & 连通（DSU 合并后单分量）& 无环（边数=点数-1 已保证）。"""
    if len(mst_edges) != V - 1:
        return False
    dsu = DisjointSetForest()
    nodes = [dsu.make_set(i) for i in range(V)]
    for _, u, v in mst_edges:
        if dsu.find_set(nodes[u]) is dsu.find_set(nodes[v]):
            return False                        # 环
        dsu.union(nodes[u], nodes[v])
    roots = {dsu.find_set(nodes[i]) for i in range(V)}
    return len(roots) == 1


def demo_mst():
    print("=" * 60)
    print("23.2 Kruskal vs Prim（电网布线：V=30 城随机图）")
    V = 30
    adj, edges = gen_connected_undirected(V, E=80, seed=3)
    mst_k, tot_k = kruskal(V, edges)
    mst_p, tot_p = prim(V, adj)
    print(f"  Kruskal: 总权 {tot_k}，{len(mst_k)} 条边 | Prim: 总权 {tot_p}，{len(mst_p)} 条边")
    print(f"  总权一致: {'✓' if tot_k == tot_p else '✗'} | Kruskal 树性: {'✓' if is_spanning_tree(V, mst_k) else '✗'}"
          f" | Prim 树性: {'✓' if is_spanning_tree(V, mst_p) else '✗'}")
    # 边集也可能不同（同权边任选），校验边集合多重集等价（权重谱）
    wk = sorted(w for w, _, _ in mst_k)
    wp = sorted(w for w, _, _ in mst_p)
    print(f"  MST 边权谱一致: {'✓' if wk == wp else '✗'}（同权多解时谱仍唯一）")

    # fuzz：随机图 70 组
    random.seed(42)
    bad = 0
    for t in range(70):
        V = random.randrange(5, 40)
        adj, edges = gen_connected_undirected(V, E=random.randrange(V, 3 * V), seed=t)
        mk, tk = kruskal(V, edges)
        mp, tp = prim(V, adj)
        if tk != tp or not is_spanning_tree(V, mk) or not is_spanning_tree(V, mp):
            bad += 1
    print(f"  70 组随机图 fuzz（互检+树性）:", "✓" if bad == 0 else f"✗ {bad} 组")


def demo_bench():
    print("=" * 60)
    print("效率：Kruskal vs Prim（E=4V，V 扫描）")
    print(f"  {'V':>7} {'Kruskal ms':>11} {'Prim ms':>9}")
    for V in (500, 1000, 2000, 4000):
        adj, edges = gen_connected_undirected(V, E=4 * V, seed=V)
        import time
        t0 = time.perf_counter()
        kruskal(V, edges)
        t_k = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        prim(V, adj)
        t_p = (time.perf_counter() - t0) * 1000
        print(f"  {V:>7} {t_k:>11.1f} {t_p:>9.1f}")
    print("  读数：Kruskal 主导成本在排序 O(E lg E)；Prim 堆操作 O(E lg V)。")
    print("  稀疏图两者接近；E→V² 时 Prim（配斐波那契堆）理论占优——见 ch19 Dijkstra 同款账。")


def main():
    demo_mst()
    demo_bench()


if __name__ == "__main__":
    main()
