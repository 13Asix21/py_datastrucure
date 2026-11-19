# -*- coding: utf-8 -*-
"""
第24章 单源最短路径 —— 24.1 Bellman-Ford + 24.2 DAG 最短路
《算法导论（原书第3版）》CLRS ch24

Bellman-Ford：允许负权边。V-1 轮松弛 + 终检判负环。O(VE)。
DAG-SHORTEST-PATHS：拓扑序一轮松弛。O(V+E)。可含负权（无环就行）。

应用：货币套汇检测（负环 = 无限套利）。
对拍：BF vs Dijkstra（非负权时三方一致）；BF 负环判定 vs 暴力环检测。
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch22_graph_algorithms"))
from ch22_02_topological_scc import topological_sort
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch19_fibonacci_heaps"))
from ch19_app_dijkstra_app import dijkstra_binary_heap


# ============================================================
# 24.1 Bellman-Ford
# ============================================================
def bellman_ford(V, edges, s):
    """edges: [(u, v, w)]。返回 (dist, 有负环?)。O(VE)"""
    INF = float("inf")
    dist = [INF] * V
    dist[s] = 0
    for _ in range(V - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                              # 提前收敛
    # 第 V 轮还能松弛 → 负环
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return dist, True
    return dist, False


# ============================================================
# 24.2 DAG 最短路
# ============================================================
def dag_shortest_paths(V, edges, s):
    """DAG-SHORTEST-PATHS：拓扑序单轮松弛。O(V+E)。图必须有向无环。"""
    from ch22_01_bfs_dfs import Graph
    g = Graph(V, directed=True)
    for u, v, w in edges:
        g.add_edge(u, v)
    order = topological_sort(g)
    if order is None:
        return None, False                      # 有环不适用
    INF = float("inf")
    dist = [INF] * V
    dist[s] = 0
    adj = [[] for _ in range(V)]
    for u, v, w in edges:
        adj[u].append((v, w))
    for u in order:
        if dist[u] == INF:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist, False


# ============================================================
# 参照：Dijkstra（复用 ch19 heapq 版）+ 暴力负环检测
# ============================================================
def has_negative_cycle_brute(V, edges):
    """暴力参照：跑 V 轮全量松弛，第 V 轮仍变化则有负可达环。
    （与 BF 判据等价但实现独立：不提前 break。）"""
    INF = float("inf")
    dist = [0] * V                  # 超源：全部 0 起跑（能到达任何负环）
    for round_i in range(V):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return False
    return True


def demo_bf_vs_dijkstra():
    print("=" * 60)
    print("24.1 Bellman-Ford vs Dijkstra（非负权三方对拍）")
    random.seed(5)
    for trial in range(8):
        V = 300
        E = 1500
        edges = []
        adj = [[] for _ in range(V)]
        for _ in range(E):
            u, v = random.randrange(V), random.randrange(V)
            if u != v:
                w = random.randrange(0, 10_000)
                edges.append((u, v, w))
                adj[u].append((v, w))
        s = random.randrange(V)
        d_bf, neg = bellman_ford(V, edges, s)
        d_di = dijkstra_binary_heap(adj, s)
        if neg or d_bf != d_di:
            print(f"  ✗ 组{trial}: BF负环={neg} 或距离不一致")
            return
    print("  8 组随机非负图（V=300）：BF == Dijkstra 逐点一致 ✓")


def demo_negative_cycle():
    print("=" * 60)
    print("24.1 负环检测 + DAG 最短路")
    # 负环样例
    edges_c = [(0,1,1),(1,2,-3),(2,0,1),(1,3,2)]
    d, neg = bellman_ford(4, edges_c, 0)
    neg2 = has_negative_cycle_brute(4, edges_c)
    print(f"  含负环图（0→1→2→0 权和 -1）: BF={neg} | 暴力={neg2}",
          "✓" if neg == neg2 == True else "✗")
    # 无负环但有负边
    edges_ok = [(0,1,4),(0,2,5),(1,2,-3),(2,3,1),(1,3,2)]
    d, neg = bellman_ford(4, edges_ok, 0)
    print(f"  负边无环图: dist={d}, neg={neg}（期望 [0, 4, 1, 2], False）",
          "✓" if d == [0, 4, 1, 2] and not neg else "✗")
    # DAG 版对照
    dd, _ = dag_shortest_paths(4, edges_ok, 0)
    print(f"  DAG-SHORTEST-PATHS 同图: dist={dd}",
          "✓" if dd == d else "✗")
    # fuzz：DAG 上两法对拍
    random.seed(9)
    bad = 0
    for t in range(50):
        V = random.randrange(5, 30)
        edges = []
        for u in range(V):
            for _ in range(random.randrange(0, 3)):
                if u + 1 < V:
                    v = random.randrange(u + 1, V)
                    edges.append((u, v, random.randrange(-50, 100)))
        if not edges:
            continue
        d1, n1 = bellman_ford(V, edges, 0)
        d2, _ = dag_shortest_paths(V, edges, 0)
        if n1 or d1 != d2:
            bad += 1
    print(f"  50 组随机 DAG（含负权）BF vs DAG 两法对拍:", "✓" if bad == 0 else f"✗ {bad} 组")


def demo_arbitrage():
    print("=" * 60)
    print("应用：货币套汇检测（负环 = 无限赚钱回路）")
    # 汇率 → 权重：w(u→v) = -log(rate)，乘法变加法、获利环变负环
    # rates[u][v] = 1 单位 u 换多少 v
    import math
    currencies = ["USD", "EUR", "GBP", "JPY", "CHF"]
    n = len(currencies)
    edges = []
    # 无套利市场：前四边用真实感汇率，第五边权取「恰好抵消」的精确值
    # （浮点汇率凑乘积=1 会有残差，直接用 -log 求和抵消，数学上环权恒 0）
    pair_w = {
        ("USD","EUR"): -math.log(0.9),
        ("EUR","GBP"): -math.log(0.85),
        ("GBP","JPY"): -math.log(150.0),
        ("JPY","CHF"): -math.log(0.008),
    }
    s4 = sum(pair_w.values())            # USD→…→CHF 的总权
    pair_w[("CHF","USD")] = -s4          # 补上使环权恰为 0（汇率 ≈ e^{s4} ≈ 1.089）
    print(f"  （补边隐含汇率 CHF→USD = {math.exp(-pair_w[('CHF','USD')]):.4f}，环乘积恰 = 1）")
    for (a, b), w in pair_w.items():
        u, v = currencies.index(a), currencies.index(b)
        edges.append((u, v, w))
        edges.append((v, u, -w))
    d, neg = bellman_ford(n, edges, 0)
    print(f"  自洽汇率市场：负环（套利）={neg}", "（应 False）", "✓" if not neg else "✗")
    # 注入歪价：某庄家 GBP→USD 报高价，形成 USD→EUR→GBP→USD 赚钱环
    edges_bad = list(edges)
    u_gbp = currencies.index("GBP")
    u_usd = currencies.index("USD")
    # 环路乘积 = 0.9*0.85*r_bad > 1 → r_bad > 1/(0.765) = 1.307
    edges_bad.append((u_gbp, u_usd, -math.log(1.35)))
    d, neg = bellman_ford(n, edges_bad, 0)
    prod = 0.9 * 0.85 * 1.35
    print(f"  注入歪价 GBP→USD@1.35（环乘积 {prod:.3f} > 1）：负环={neg}",
          "✓" if neg else "✗")
    print("  读数：把汇率取 -log 变边权，赚钱环 ⇔ 乘积>1 ⇔ 权和<0 ⇔ 负环。")
    print("        Bellman-Ford 一遍就能告诉你哪里能无限套利——真实外汇市场的套利检测内核。")


def main():
    demo_bf_vs_dijkstra()
    demo_negative_cycle()
    demo_arbitrage()


if __name__ == "__main__":
    main()
