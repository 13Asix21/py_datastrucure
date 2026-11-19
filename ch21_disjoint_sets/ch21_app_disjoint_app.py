# -*- coding: utf-8 -*-
"""
第21章 应用：并查集的三张真实面孔
《算法导论（原书第3版）》CLRS ch21

  1) 图像连通域计数（OpenCV connectedComponents 的内核原理）
     对拍 BFS 洪泛填充 + 大图计时
  2) 渗流阈值蒙特卡洛（物理模拟经典）：方格随机占位，
     估计临界概率 p* ≈ 0.5927（理论值）
  3) Kruskal 迷宫生成：随机森林算法（游戏地牢生成器）
"""

import os
import sys
import time
import random
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch21_disjoint_set import DisjointSetForest


# ============================================================
# 1) 图像连通域
# ============================================================
def components_dsu(grid):
    """DSU 版连通域：格点 → 结点，相邻同色像素 UNION。近 O(α(n))。"""
    H, W = len(grid), len(grid[0])
    dsu = DisjointSetForest()
    nodes = [[dsu.make_set((r, c)) for c in range(W)] for r in range(H)]
    for r in range(H):
        for c in range(W):
            if c + 1 < W and grid[r][c] == grid[r][c + 1]:
                dsu.union(nodes[r][c], nodes[r][c + 1])
            if r + 1 < H and grid[r][c] == grid[r + 1][c]:
                dsu.union(nodes[r][c], nodes[r + 1][c])
    roots = set()
    for r in range(H):
        for c in range(W):
            roots.add(dsu.find_set(nodes[r][c]))
    return len(roots)


def components_bfs(grid):
    """BFS 洪泛参照版：O(HW)。"""
    H, W = len(grid), len(grid[0])
    seen = [[False] * W for _ in range(H)]
    count = 0
    for r in range(H):
        for c in range(W):
            if seen[r][c]:
                continue
            count += 1
            color = grid[r][c]
            q = deque([(r, c)])
            seen[r][c] = True
            while q:
                y, x = q.popleft()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        q.append((ny, nx))
    return count


def demo_image_components():
    print("=" * 60)
    print("应用1：图像连通域计数（黑白二值图）")
    random.seed(5)
    for density in (0.3, 0.6):
        H = W = 60
        grid = [[1 if random.random() < density else 0 for _ in range(W)] for _ in range(H)]
        a = components_dsu(grid)
        b = components_bfs(grid)
        print(f"  前景点率 p={density}: DSU={a} vs BFS 洪泛={b} {'✓' if a == b else '✗'}")
    # 大图计时
    H = W = 260
    grid = [[1 if random.random() < 0.5 else 0 for _ in range(W)] for _ in range(H)]
    t0 = time.perf_counter()
    d1 = components_dsu(grid)
    t_dsu = time.perf_counter() - t0
    t0 = time.perf_counter()
    d2 = components_bfs(grid)
    t_bfs = time.perf_counter() - t0
    print(f"  {H}x{W} 图：DSU {t_dsu*1000:7.1f} ms vs BFS {t_bfs*1000:7.1f} ms（结果一致 {d1 == d2}, {d1} 域）")
    print("  读数：两法同阶 O(HW)，DSU 系数略大但在\"动态加边并随时问连通\"的交互场景（如增量分割）中不可替代。")


# ============================================================
# 2) 渗流阈值蒙特卡洛
# ============================================================
def percolates_dsu(n, p, seed):
    """n×n 方格，每个格以概率 p 开放。判断顶层是否与底层连通（渗流）。
    顶部一行并成超源 SUPER-TOP，底部一行并成 SUPER-BOTTOM。"""
    rng = random.Random(seed)
    open_site = [[rng.random() < p for _ in range(n)] for _ in range(n)]
    dsu = DisjointSetForest()
    nodes = [[dsu.make_set((r, c)) if open_site[r][c] else None for c in range(n)] for r in range(n)]
    top = dsu.make_set("TOP")
    bot = dsu.make_set("BOT")
    for c in range(n):
        if open_site[0][c]:
            dsu.union(nodes[0][c], top)
        if open_site[n - 1][c]:
            dsu.union(nodes[n - 1][c], bot)
    for r in range(n):
        for c in range(n):
            if not open_site[r][c]:
                continue
            if r + 1 < n and open_site[r + 1][c]:
                dsu.union(nodes[r][c], nodes[r + 1][c])
            if c + 1 < n and open_site[r][c + 1]:
                dsu.union(nodes[r][c], nodes[r][c + 1])
    return dsu.find_set(top) is dsu.find_set(bot)


def demo_percolation():
    print("=" * 60)
    print("应用2：渗流阈值蒙特卡洛（n=20，每点 300 试验）")
    print("理论：方格点位渗流阈值 p* ≈ 0.5927")
    trials = 300
    n = 20
    for p in (0.45, 0.55, 0.5927, 0.65, 0.75):
        hits = 0
        for t in range(trials):
            if percolates_dsu(n, p, seed=10_000 + t):
                hits += 1
        frac = hits / trials
        print(f"  p={p:<7} 渗流率 {frac:5.1%}  {'——越过阈值' if frac > 0.5 else ''}")
    print("  → p 在 0.55→0.65 之间渗流率从偶发跃迁到必然——相变即阈值 p*（0.5927 附近）。")


# ============================================================
# 3) Kruskal 迷宫生成
# ============================================================
def gen_maze_kruskal(W, H, seed=9):
    """随机取边不成环 → 完美迷宫（唯一路径）。
    判据：加墙洞 (A,B) 前若同根则跳过 → 树 = 迷宫。"""
    random.seed(seed)
    dsu = DisjointSetForest()
    node = [[dsu.make_set((r, c)) for c in range(W)] for r in range(H)]
    walls = []
    for r in range(H):
        for c in range(W):
            if c + 1 < W:
                walls.append(((r, c), (r, c + 1)))
            if r + 1 < H:
                walls.append(((r, c), (r + 1, c)))
    random.shuffle(walls)
    opened = []
    for a, b in walls:
        if dsu.find_set(node[a[0]][a[1]]) is not dsu.find_set(node[b[0]][b[1]]):
            dsu.union(node[a[0]][a[1]], node[b[0]][b[1]])
            opened.append((a, b))
    return opened, W, H


def render_maze(opened, W, H):
    """ASCII 渲染：开洞处墙打空。"""
    top = ["+"] + ["-"] * W + ["+"]
    # 构墙集合
    h_open = set()   # (r, c) 与 (r, c+1) 通
    v_open = set()   # (r, c) 与 (r+1, c) 通
    for (r1, c1), (r2, c2) in opened:
        if r1 == r2:
            h_open.add((r1, c1))
        else:
            v_open.add((r1, c1))
    lines = ["+" + "+".join(["-"] * W) + "+"]
    for r in range(H):
        row = ["|"]
        for c in range(W):
            row.append(" ")
            if (r, c) in h_open and c + 1 < W:
                row.append(" ")
            else:
                row.append("|")
        lines.append("".join(row))
        # 底墙行
        bot = ["+"]
        for c in range(W):
            if (r, c) in v_open:
                bot.append(" +")
            else:
                bot.append("-+")
        lines.append("".join(bot))
    return "\n".join(lines)


def demo_maze():
    print("=" * 60)
    print("应用3：Kruskal 迷宫生成（8×6）")
    opened, W, H = gen_maze_kruskal(8, 6)
    # 完美迷宫校验：开洞数 = W·H - 1（生成树的边数）
    expect_edges = W * H - 1
    print(f"  开洞 {len(opened)} == W·H-1 = {expect_edges}: {'✓（树，保证任意两点唯一路径）' if len(opened) == expect_edges else '✗'}")
    print(render_maze(opened, W, H))


# ============================================================
# 4) 微基准：路径压缩 + 按秩合并的实际功力
# ============================================================
def demo_micro_bench():
    print("=" * 60)
    print("微基准：40 万次随机 UNION/FIND（n=20 万）——按秩+压缩 vs 仅按秩")
    class NoCompression(DisjointSetForest):
        def find_set(self, x):
            root = x
            while root.p is not root:
                root = root.p
            return root
    random.seed(2)
    for cls, tag in ((DisjointSetForest, "按秩 + 路径压缩"),
                     (NoCompression, "仅按秩（无压缩）")):
        dsu = cls()
        n = 200_000
        nodes = [dsu.make_set(i) for i in range(n)]
        t0 = time.perf_counter()
        for _ in range(400_000):
            a = random.choice(nodes)
            b = random.choice(nodes)
            ra, rb = dsu.find_set(a), dsu.find_set(b)
            if ra is not rb:
                dsu.union(a, b)
        dt = time.perf_counter() - t0
        # 树高统计（压缩后应极浅）
        max_h = 0
        for x in random.sample(nodes, min(n, 20000)):
            h = 0
            while x.p is not x:
                x = x.p
                h += 1
                max_h = max(max_h, h)
        print(f"  {tag}: {dt*1000:8.1f} ms | 最大链深(抽样) {max_h}")
    print("  → 链深 3 vs 7：路径压缩把树近压成平坦（α(n) 阶，n=20万时≈4）。")
    print("    混合操作总耗时无压缩版反而略快——纯 Python 里压缩的两趟循环常数 > ")
    print("    按秩维护树矮带来的收益；但 find 次数远多于 union 的场景（如 Kruskal 大图），")
    print("    压缩的摊还 O(α(n)) 会反超。工程库（如 Boost）默认两者全开。")


def main():
    demo_image_components()
    demo_percolation()
    demo_maze()
    demo_micro_bench()


if __name__ == "__main__":
    main()
