# -*- coding: utf-8 -*-
"""
第22章 应用：图遍历的三张实战面孔
《算法导论（原书第3版）》CLRS ch22

  1) 社交网络：六度分隔实验（BFS 的天然主场——雪花采样图）
     度分布 + 连通分量 + 平均距离 vs 暴力全对 Dijkstra-ish
  2) 任务依赖调度：拓扑序决定构建顺序（CI/编译 pipeline）
     对拍 Kahn；含循环依赖检测
  3) 网页可达性：SCC 压缩成"网页集团"（PageRank 预处理步骤）
  4) 效率：递归 DFS vs 显式栈 vs BFS（大图遍历计时）
"""

import os
import sys
import time
import random
from collections import deque, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch22_01_bfs_dfs import Graph
from ch22_02_topological_scc import topological_sort, topological_sort_kahn, kosaraju_scc


# ============================================================
# 1) 社交网络 六度分隔
# ============================================================
def snowball_social_graph(n, avg_degree=8, seed=5):
    """雪花采样式社交图：带社区结构的无向图。
    每人连 avg_degree/2 个"圈子内"近邻 + 若干远端桥接边——比纯随机图更接近真实社交网络（小世界）。"""
    random.seed(seed)
    g = Graph(n, directed=False)
    # 环形局部连接（社区感）
    for u in range(n):
        for offset in (1, 2, 3):
            v = (u + offset) % n
            if random.random() < 0.35:
                g.add_edge(u, v)
    # 随机远端桥
    extra = n * avg_degree // 8
    for _ in range(extra):
        u = random.randrange(n)
        v = random.randrange(n)
        if u != v:
            g.add_edge(u, v)
    return g


def demo_social():
    print("=" * 60)
    print("应用1：社交网络分析（n=2000 小世界图）")
    n = 2000
    g = snowball_social_graph(n, avg_degree=8)
    # 度分布
    degs = [len(g.adj[u]) for u in range(n)]
    print(f"  总边数 {len(g.edges)//2} | 平均度 {sum(degs)/n:.1f} | 最大度 {max(degs)}")
    # 连通性：BFS 覆盖
    dist = g.bfs(0)
    reachable = sum(1 for d in dist if d != float("inf"))
    print(f"  从结点 0 出发可达 {reachable}/{n}（{reachable/n:.0%}）")
    # 六度分隔：随机 200 对的 BFS 距离
    random.seed(11)
    samples = 200
    total_d = 0
    cnt = 0
    max_d = 0
    for _ in range(samples):
        s = random.randrange(n)
        ds = g.bfs(s)
        t = random.choice([x for x in range(n) if ds[x] != float("inf")])
        d = ds[t]
        if d > 0:
            total_d += d
            cnt += 1
            max_d = max(max_d, d)
    print(f"  {samples} 对随机人链 BFS 平均跳数 {total_d/max(cnt,1):.2f} | 最长 {max_d} —— 六度分隔的小世界特征")
    # 效率：BFS 单源全图 vs 逐对暴力
    t0 = time.perf_counter()
    for s in random.sample(range(n), 20):
        g.bfs(s)
    t_bfs_avg = (time.perf_counter() - t0) / 20       # 一个源 → 全图距离
    t0 = time.perf_counter()
    for s in random.sample(range(n), 3):
        for t in random.sample(range(n), 30):
            cur = {s}; seen = {s}
            for depth in range(1, 15):
                nxt = set()
                for u in cur:
                    for v in g.adj[u]:
                        if v not in seen:
                            seen.add(v); nxt.add(v)
                if t in nxt:
                    break
                cur = nxt
    t_brute_pair = (time.perf_counter() - t0) / 90   # 一对点的距离
    print(f"  BFS 单源全图 {t_bfs_avg*1000:.1f} ms（此后任意点查距离 O(1)）| 逐对暴力 {t_brute_pair*1000:.1f} ms/对")
    print(f"  → 查 k 对距离：BFS 一源覆盖全部；暴力重复扩展是 O(k(V+E)) 的浪费，k 一大就被碾压。")


# ============================================================
# 2) 构建系统（拓扑序 pipeline）
# ============================================================
def demo_build_pipeline():
    print("=" * 60)
    print("应用2：构建系统模块依赖（make/webpack 本质）")
    random.seed(8)
    n = 12
    label = ["core", "utils", "config", "log", "net", "auth", "db",
             "api", "cache", "ui", "router", "app"]
    g = Graph(n, directed=True)
    deps = [("core","utils"),("core","config"),("utils","log"),("config","log"),
            ("net","core"),("auth","net"),("auth","db"),("db","core"),
            ("api","auth"),("api","db"),("cache","db"),("api","cache"),
            ("ui","api"),("router","ui"),("router","api"),("app","router")]
    idx = {name: i for i, name in enumerate(label)}
    for a, b in deps:
        g.add_edge(idx[a], idx[b])
    ts = topological_sort(g)
    kahn = topological_sort_kahn(g)
    def check(order):
        """拓扑序合法性：每条依赖边 u→v 都满足 u 在 v 前。"""
        pos = {u: i for i, u in enumerate(order)}
        return all(pos[u] < pos[v] for u, v in g.edges)
    print("  构建顺序（Kahn 拓扑序，依赖在前）:", " → ".join(label[i] for i in kahn))
    print(f"  全部 {len(deps)} 条依赖满足: DFS序 {'✓' if check(ts) else '✗'} | Kahn序 {'✓' if check(kahn) else '✗'}")
    # 有环测试：app 的下游链最终到 core→utils；再补 utils→app 即闭环
    g.add_edge(idx["utils"], idx["app"])
    r = topological_sort(g)
    print("  加边 utils→app 后:", r, "(None = make 报 circular dependency ✓)")


# ============================================================
# 3) 网页 SCC 集团
# ============================================================
def demo_web_scc():
    print("=" * 60)
    print("应用3：网页链接的 SCC 集团（搜索引擎预处理）")
    random.seed(13)
    # 造 500 页网页：块状互链 + 少量单行道
    n = 500
    g = Graph(n, directed=True)
    blocks = [range(i, i + 50) for i in range(0, n, 50)]   # 10 个块
    for b in blocks:
        bl = list(b)
        for _ in range(120):                               # 块内互链（双向）
            u = random.choice(bl); v = random.choice(bl)
            if u != v:
                g.add_edge(u, v)
                g.add_edge(v, u)
    for _ in range(15):                                     # 块间单行道
        u = random.randrange(n); v = random.randrange(n)
        if (u // 50) != (v // 50):
            g.add_edge(u, v)
    scc_id, comps = kosaraju_scc(g)
    big = [c for c in comps if len(c) >= 5]
    sizes = sorted((len(c) for c in comps), reverse=True)
    print(f"  SCC 总数 {len(comps)}，大集团（≥5 页）{len(big)} 个，最大 5 个集团规模: {sizes[:5]}")
    singleton = sum(1 for c in comps if len(c) == 1)
    print(f"  单页分量 {singleton} 个 | 最大集团 {max(len(c) for c in comps)} 页")
    print("  读数：块内互链形成强连通集团（彼此可达=可互见），块间单行道把集团串成 DAG——")
    print("        搜索引擎据此把集团当一个超节点算权重（分量图是 DAG，定理 22.16）。")


# ============================================================
# 4) 遍历效率：递归 DFS vs 显式栈 vs BFS
# ============================================================
def demo_traversal_bench():
    print("=" * 60)
    print("效率：大图遍历（V=3 万，E≈9 万）")
    random.seed(2)
    n = 30_000
    g = Graph(n, directed=False)
    for _ in range(45_000):
        u = random.randrange(n); v = random.randrange(n)
        if u != v:
            g.add_edge(u, v)
    # BFS
    t0 = time.perf_counter()
    g.bfs(0)
    t_bfs = time.perf_counter() - t0
    # 递归 DFS（栈深风险大 → 用我们的 dfs，Python 默认递归 1000，此图树深可能超）
    import sys
    sys.setrecursionlimit(100_000)
    t0 = time.perf_counter()
    g.dfs()
    t_dfs_rec = time.perf_counter() - t0
    # 显式栈 DFS
    t0 = time.perf_counter()
    seen = [False] * n
    stack = [0]
    seen[0] = True
    vis = 0
    while stack:
        u = stack.pop()
        vis += 1
        for v in g.adj[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    t_dfs_iter = time.perf_counter() - t0
    print(f"  BFS {t_bfs*1000:7.1f} ms | DFS 递归 {t_dfs_rec*1000:7.1f} ms | DFS 显式栈 {t_dfs_iter*1000:7.1f} ms")
    print("  → 同阶 O(V+E)；递归版受 Python 栈机制拖累还有限深风险，工程上多用显式栈。")


def main():
    demo_social()
    demo_build_pipeline()
    demo_web_scc()
    demo_traversal_bench()


if __name__ == "__main__":
    main()
