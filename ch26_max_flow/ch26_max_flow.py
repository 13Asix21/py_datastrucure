# -*- coding: utf-8 -*-
"""
第26章 最大流 —— Edmonds-Karp（BFS 增广）
《算法导论（原书第3版）》CLRS ch26

Ford-Fulkerson 方法 + BFS 选最短增广路 = Edmonds-Karp。O(V·E²)。
最大流最小割定理（26.7）：流值 = 割容量。

应用：二分图匹配（26.3 匹配问题 ⇔ 最大流）——任务分配。
对拍：流值一致性（独立跑两次）+ 残量网络无增广路校验 + 割验证
     + 二分匹配对拍贪心近似（验证"最大"二字的含金量）。
"""

import os
import sys
import random
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class FlowNetwork:
    """残量网络表示：capacity[u][v]，flow 隐含于残量。"""

    def __init__(self, V):
        self.V = V
        self.capacity = [dict() for _ in range(V)]   # u -> {v: cap}

    def add_edge(self, u, v, cap):
        """正向容量 cap，反向容量 0（残量网络双条边）。"""
        self.capacity[u][v] = self.capacity[u].get(v, 0) + cap
        self.capacity[v].setdefault(u, 0)              # 反向边（可能已有平行边）

    def edmonds_karp(self, s, t):
        """返回最大流值；self.capacity 被改成最终残量网络。O(VE²)"""
        total = 0
        while True:
            # BFS 找 s→t 最短增广路
            parent = [None] * self.V
            parent[s] = s
            q = deque([s])
            while q and parent[t] is None:
                u = q.popleft()
                for v, cap in self.capacity[u].items():
                    if cap > 0 and parent[v] is None:
                        parent[v] = u
                        if v == t:
                            break
                        q.append(v)
            if parent[t] is None:
                break                                  # 无增广路 → 结束
            # 找路径瓶颈
            bottleneck = float("inf")
            v = t
            while v != s:
                u = parent[v]
                bottleneck = min(bottleneck, self.capacity[u][v])
                v = u
            # 沿路增广
            v = t
            while v != s:
                u = parent[v]
                self.capacity[u][v] -= bottleneck
                self.capacity[v][u] = self.capacity[v].get(u, 0) + bottleneck
                v = u
            total += bottleneck
        return total

    def min_cut_after_maxflow(self, s):
        """最大流跑完后：s 可达（残量>0）的点集 = 最小割 S 侧。"""
        seen = [False] * self.V
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for v, cap in self.capacity[u].items():
                if cap > 0 and not seen[v]:
                    seen[v] = True
                    q.append(v)
        return seen                                     # S = {v: seen[v]}


def demo_maxflow_basics():
    print("=" * 60)
    print("26.2 Edmonds-Karp（教科书图 26.1 同款流网络）")
    # CLRS Figure 26.1: s=v0, v1..v4, t=v5
    fn = FlowNetwork(6)
    E = [(0,1,16),(0,2,13),(1,3,12),(2,1,4),(3,2,9),(2,4,14),(4,3,7),(3,5,20),(4,5,4)]
    for u, v, c in E:
        fn.add_edge(u, v, c)
    flow = fn.edmonds_karp(0, 5)
    print(f"  最大流 = {flow}（教科书答案 23）", "✓" if flow == 23 else "✗")
    # 最小割
    S = fn.min_cut_after_maxflow(0)
    cut_edges = [(u, v, c) for (u, v, c) in E if S[u] and not S[v]]
    cut_cap = sum(c for _, _, c in cut_edges)
    print(f"  最小割点集 S = {[i for i in range(6) if S[i]]}")
    print(f"  割边: {cut_edges}，容量和 = {cut_cap}",
          "✓ == 最大流（最小割定理）" if cut_cap == flow else "✗")
    # 无增广路校验：再跑一次应当返回 0
    fn2 = FlowNetwork(6)
    for u, v, c in E:
        fn2.add_edge(u, v, c)
    f_first = fn2.edmonds_karp(0, 5)
    f_second = fn2.edmonds_karp(0, 5)
    print(f"  增广轮结束后再跑: 追加流 {f_second}（应 0）", "✓" if f_second == 0 and f_first == 23 else "✗")


def demo_bipartite_matching():
    print("=" * 60)
    print("26.3 应用：二分图匹配（任务分配，最大流建模）")
    # 建模：tasks(5) —(能做,1)— workers(4)；源→task 1，worker→汇 1
    random.seed(6)
    n_tasks, n_workers = 60, 8
    # 随机技能矩阵
    can = [[random.random() < (0.35 if w < 8 else 0) for w in range(n_workers)] for _ in range(n_tasks)]
    V = 1 + n_tasks + n_workers + 1
    s, t = 0, V - 1
    fn = FlowNetwork(V)
    for i in range(n_tasks):
        fn.add_edge(s, 1 + i, 1)
        for w in range(n_workers):
            if can[i][w]:
                fn.add_edge(1 + i, 1 + n_tasks + w, 1)
    for w in range(n_workers):
        fn.add_edge(1 + n_tasks + w, t, 1)
    flow = fn.edmonds_karp(s, t)
    # 提取匹配：task i → worker w（残量网络里反向边有流）
    matching = {}
    for i in range(n_tasks):
        for w in range(n_workers):
            v = 1 + n_tasks + w
            if fn.capacity[v].get(1 + i, 0) > 0:    # 反向边残量=1 → 有流
                matching[i] = w
    # 校验：每人至多一个任务；匹配数 == flow
    workers_used = list(matching.values())
    ok_unique = len(workers_used) == len(set(workers_used))
    ok_count = len(matching) == flow
    # 全部匹配边都是真实技能边
    ok_skill = all(can[i][w] for i, w in matching.items())
    # 贪心参照（顺序贪心不保证最大）
    greedy_used = set()
    greedy_cnt = 0
    for i in range(n_tasks):
        for w in range(n_workers):
            if can[i][w] and w not in greedy_used:
                greedy_used.add(w)
                greedy_cnt += 1
                break
    print(f"  最大匹配 = {flow}/{n_workers}（{n_tasks} 个任务抢 {n_workers} 个工人）")
    print(f"  匹配唯一性 {'✓' if ok_unique else '✗'} | 数量一致 {'✓' if ok_count else '✗'} | 全真实技能边 {'✓' if ok_skill else '✗'}")
    print(f"  顺序贪心对照: {greedy_cnt}（最大流 {'≥' if flow >= greedy_cnt else '<'} 贪心",
          "— 贪心可能吃亏，最大流给出真正上界" if flow >= greedy_cnt else "!")


def main():
    demo_maxflow_basics()
    demo_bipartite_matching()


if __name__ == "__main__":
    main()
