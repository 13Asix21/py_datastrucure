# -*- coding: utf-8 -*-
"""
第19章 应用：斐波那契堆驱动 Dijkstra 最短路径
《算法导论（原书第3版）》CLRS ch19（应用场景承接 ch24.3）

Dijkstra 的性能心脏 = 优先队列。三种实现同台：
  A) 朴素数组线性扫 min       O(V²)
  B) 二叉堆（heapq，C 实现）  O((V+E) lg V)
  C) 斐波那契堆（ch19 自实现，DECREASE-KEY 摊还 O(1)）
     → 教科书 24.3：O(E + V lg V)，稠密图理论最优

三实现逐点对拍正确性 + 三种规模计时。
"""

import os
import sys
import time
import heapq
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch19_fib_heap import FibonacciHeap


def random_graph(V, E, seed=1, max_w=10_000):
    """随机连通有向图：先铺生成树骨架（保证连通），再补随机边。"""
    random.seed(seed)
    adj = [[] for _ in range(V)]
    for v in range(1, V):
        u = random.randrange(v)
        adj[u].append((v, random.randrange(1, max_w)))
    extra = E - (V - 1)
    for _ in range(max(extra, 0)):
        u = random.randrange(V)
        v = random.randrange(V)
        if u != v:
            adj[u].append((v, random.randrange(1, max_w)))
    return adj


# ============================================================
# A) 朴素 O(V²)
# ============================================================
def dijkstra_naive(adj, src):
    V = len(adj)
    INF = float("inf")
    dist = [INF] * V
    dist[src] = 0
    done = [False] * V
    for _ in range(V):
        u, best = -1, INF
        for v in range(V):
            if not done[v] and dist[v] < best:
                u, best = v, dist[v]
        if u == -1:
            break
        done[u] = True
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


# ============================================================
# B) 二叉堆 + 惰性删除（heapq）
# ============================================================
def dijkstra_binary_heap(adj, src):
    V = len(adj)
    INF = float("inf")
    dist = [INF] * V
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                      # 过期条目（惰性删除）
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


# ============================================================
# C) 斐波那契堆：教科书式显式 DECREASE-KEY
# ============================================================
def dijkstra_fib_heap(adj, src):
    V = len(adj)
    INF = float("inf")
    dist = [INF] * V
    h = FibonacciHeap()
    node_of = [None] * V

    dist[src] = 0
    for v in range(V):
        node_of[v] = h.insert(0 if v == src else INF, payload=v)
    in_tree = [False] * V

    while h.n > 0:
        u_node = h._extract_min_node()
        u = u_node.payload
        if in_tree[u]:
            continue                       # INF 结点冗余提取保护
        in_tree[u] = True
        if dist[u] == INF:
            continue
        for v, w in adj[u]:
            if not in_tree[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                h.decrease_key(node_of[v], dist[v])   # 招牌：O(1) 摊还
    return dist


def main():
    print("=" * 60)
    print("应用：Dijkstra 三实现 — 正确性对拍 + 规模计时")

    # ---------- 正确性 ----------
    print("-" * 60)
    print("正确性对拍（V=300, E=3000，10 组随机图+随机源）:")
    bad = 0
    for t in range(10):
        V, E = 300, 3000
        adj = random_graph(V, E, seed=100 + t)
        src = random.randrange(V)
        d1 = dijkstra_naive(adj, src)
        d2 = dijkstra_binary_heap(adj, src)
        d3 = dijkstra_fib_heap(adj, src)
        if not (d1 == d2 == d3):
            bad += 1
            diff = [(i, d1[i], d2[i], d3[i])
                    for i in range(V) if d1[i] != d2[i] or d2[i] != d3[i]][:3]
            print(f"  ✗ 组{t} 源{src} 差异样例: {diff}")
    print(f"  10 组三方逐点对拍: {'✓ 全部一致' if bad == 0 else f'✗ {bad} 组不一致'}")

    # ---------- 效率 ----------
    print("-" * 60)
    print("效率计时（E = 4V，源=0，单位 ms）:")
    print(f"  {'V':>6} {'朴素 O(V²)':>12} {'heapq 二叉堆':>14} {'斐波那契堆(纯Py)':>18}")
    for V in (500, 1000, 2000, 4000):
        adj = random_graph(V, 4 * V, seed=7)
        t0 = time.perf_counter()
        dijkstra_naive(adj, 0)
        t1 = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        dijkstra_binary_heap(adj, 0)
        t2 = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        dijkstra_fib_heap(adj, 0)
        t3 = (time.perf_counter() - t0) * 1000
        print(f"  {V:>6} {t1:>12.1f} {t2:>14.1f} {t3:>18.1f}")
    print("  读数解读：")
    print("  · heapq 是 C 实现的工业二叉堆，纯 Python 斐波那契堆常数大——工程上 heapq 碾压；")
    print("  · 但理论账要算清：斐 DECREASE-KEY 摊还 O(1) → 稠密图(Θ(V²)边)复杂度 O(E+V lgV) 优于二叉堆 O(E lgV)；")
    print("  · 朴素版在稠密图反而是最优（免堆开销）——选结构先看图的密度。")


if __name__ == "__main__":
    main()
