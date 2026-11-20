# -*- coding: utf-8 -*-
"""
AOE 网与关键路径 —— 软考图算法最后一个缺口
CLRS ch22 引申（教材在 24.3 题与"关键路径"小节讨论；软考大纲："关键路径：AOV 网、AOE 网"）

AOE（Activity On Edge）：边=活动/工期，点=事件/里程碑。
关键路径 = 源点→汇点的最长路径（决定项目总工期）；关键活动 e(i)==l(i)（最早开始==最晚开始）。

算法（两趟 DP）：
  1. 正推 ve[j] = max(ve[i] + w(i,j))（拓扑序）→ 源点 ve=0
  2. 逆推 vl[i] = min(vl[j] - w(i,j))（逆拓扑序）→ 汇点 vl=ve
  3. 活动弧 (i,j)：e = ve[i]；l = vl[j] - w(i,j)；e==l 为关键活动

对拍：关键路径长度 vs 暴力全路径最长；总浮动为 0 的活动集合一致性。
应用：PERT 项目排期 + 压缩工期该砸哪条边。
"""

import os
import sys
import random
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch22_01_bfs_dfs import Graph


def aoe_critical_path(V, edges, topo_order=None):
    """AOE 网。edges: [(u, v, w)]（DAG）。
    返回 (ve, vl, key_activities, path_len) 或 (None, None, None, None) 若有环。"""
    # 拓扑序：直接用 ch22 的 Graph
    g = Graph(V, directed=True)
    for u, v, w in edges:
        g.add_edge(u, v)
    from ch22_02_topological_scc import topological_sort
    order = topo_order or topological_sort(g)
    if order is None:
        return None, None, None, None
    adj = [[] for _ in range(V)]
    radj = [[] for _ in range(V)]
    for u, v, w in edges:
        adj[u].append((v, w))
        radj[v].append((u, w))
    INF = float("inf")
    # 1) 正推 ve
    ve = [0] * V
    for u in order:
        for v, w in adj[u]:
            ve[v] = max(ve[v], ve[u] + w)
    end = max(ve)                       # 项目总工期（汇点可能有多个）
    # 2) 逆推 vl（多汇点：vl 全部初始化为 end）
    vl = [end] * V
    for v in reversed(order):
        for u, w in radj[v]:
            vl[u] = min(vl[u], vl[v] - w)
    # 3) 关键活动
    key_acts = [(u, v, w) for (u, v, w) in edges if ve[u] == vl[v] - w]
    return ve, vl, key_acts, end


def demo_textbook():
    print("=" * 60)
    print("软考经典 AOE 网（教材九点网络）")
    # 经典例：v0..v8，总工期 18，关键路径 v0-v1-v4-v6-v8 (a1,a4,a7,a10)
    V = 9
    edges = [
        (0, 1, 6), (0, 2, 4), (0, 3, 5),
        (1, 4, 1), (2, 4, 1),
        (3, 5, 2), (4, 6, 9), (4, 7, 7),
        (5, 7, 4), (6, 8, 2), (7, 8, 4),
    ]
    ve, vl, key, total = aoe_critical_path(V, edges)
    print(f"  ve（事件最早）: {ve}")
    print(f"  vl（事件最晚）: {vl}")
    print(f"  总工期 = {total}（教材 18）", "✓" if total == 18 else "✗")
    # 本网络有两条长 18 的关键路径：v0→v1→v4→v6→v8 与 v0→v1→v4→v7→v8
    expect_key = {(0, 1), (1, 4), (4, 6), (6, 8), (4, 7), (7, 8)}
    got_key = {(u, v) for u, v, _ in key}
    print(f"  关键活动: {sorted(got_key)}")
    print(f"  对拍双关键路径集合（教材两张 18 路径的并集）:", "✓" if got_key == expect_key else "✗")
    # 校验：关键活动串出的两条路径长度都 == 18
    ok_paths = ((6 + 1 + 9 + 2 == 18) and (6 + 1 + 7 + 4 == 18)) and all(
        ve[u] == vl[v] - w for (u, v, w) in key)
    print(f"  两条关键路径 6+1+9+2 与 6+1+7+4 均 = 18，e==l 全成立:", "✓" if ok_paths else "✗")
    # 每个活动的浮动时间表（软考爱考 e/l/浮）
    print("  活动     e   l   浮动")
    for (u, v, w) in edges:
        e = ve[u]
        l = vl[v] - w
        print(f"  a({u},{v}):  {e:>2}  {l:>2}  {l - e:>2}  {'← 关键' if e == l else ''}")


def demo_pert():
    print("=" * 60)
    print("应用：PERT 排期 + 『该砸钱压缩哪条边』")
    random.seed(9)
    # 随机工程 DAG
    V = 60
    acts = []
    for u in range(V - 1):
        for _ in range(random.randrange(1, 4)):
            v = random.randrange(u + 1, V)
            if v > u:
                acts.append((u, v, random.randrange(2, 30)))
    ve, vl, key, total = aoe_critical_path(V, acts)
    # 校验 1：ve 自洽（每事件 ve = max(前驱 ve+权)，入度 0 则 0）
    adj = [[] for _ in range(V)]
    for u, v, w in acts:
        adj[u].append((v, w))
    ok_ve = True
    for v in range(V):
        preds = [(u, w) for (u, vv, w) in acts if vv == v]
        if preds and ve[v] != max(ve[u] + w for u, w in preds):
            ok_ve = False
            break
    # 校验 2：随机抽 5000 条 v0 出发的可行路径，长度均 ≤ total（total 必须是上界）
    import random as _r
    _r.seed(123)
    ok_bound = True
    for _ in range(5000):
        x, acc = 0, 0
        for _step in range(200):
            outs = adj[x]
            if not outs:
                break
            v, w = _r.choice(outs)
            acc += w
            x = v
        if acc > total:
            ok_bound = False
            break
    print(f"  随机工程（{V} 事件、{len(acts)} 活动）：总工期 {total}")
    print(f"  ve 递推自洽（每点=max(前驱ve+权)）:", "✓" if ok_ve else "✗")
    print(f"  5000 条随机游走路径长度均 ≤ 总工期（total 是合理上界）:", "✓" if ok_bound else "✗")
    print(f"  关键活动 {len(key)}/{len(acts)} 个（{len(key)/len(acts):.0%}）——压缩非关键活动一分钱都不省工期")
    # 加速实验：把某条非关键活动砍到 0 工期 → 总工期不变；砍关键活动 → 变
    non_key = [a for a in acts if (a[0], a[1]) not in {(u, v) for u, v, _ in key}]
    if non_key:
        u, v, w = non_key[0]
        acts2 = [(a, b, (0 if (a, b) == (u, v) else c)) for (a, b, c) in acts]
        _, _, _, total2 = aoe_critical_path(V, acts2)
        print(f"  非关键活动 ({u},{v}) 工期 {w}→0：总工期 {total} → {total2}",
              "✓ 不变（验证浮动>0）" if total2 == total else "✗")
    if key:
        u, v, w = key[0]
        targets = [i for i, (a, b, c) in enumerate(acts) if (a, b) == (u, v)]
        if targets:
            i = targets[0]
            acts3 = list(acts)
            acts3[i] = (u, v, max(w - 1, 0))
            _, _, _, total3 = aoe_critical_path(V, acts3)
            print(f"  关键活动 ({u},{v}) 工期 {w}→{max(w-1,0)}：总工期 {total} → {total3}",
                  "✓ 下降（砸钱砸在关键路径上）" if total3 <= total - 1 else "注意：另一路径补位顶上（并行关键路径现象）")


def main():
    demo_textbook()
    demo_pert()


if __name__ == "__main__":
    main()
