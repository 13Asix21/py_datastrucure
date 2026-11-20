# -*- coding: utf-8 -*-
"""
第15章 动态规划 —— 钢条切割 / 矩阵链乘 / LCS / 0-1背包
《算法导论（原书第3版）》CLRS ch15

DP 四步方法论（15.1 引入）：刻画最优解结构 → 递归定义 → 自底向上计算 → 构造解。
四个标本：
  15.1 钢条切割（自顶向下 memo vs 自底向上）
  15.2 矩阵链乘（区间 DP + 最优括号化打印）
  15.4 LCS（最长公共子序列 + 方向回溯）
  15.4 引申 0-1 背包

应用：git diff 的本质就是 LCS。
对拍：暴力枚举参照 / 各章教科书标准答案。
"""

import random
import time
from functools import lru_cache


# ============================================================
# 15.1 钢条切割
# ============================================================
def cut_rod_naive(p, n):
    """自顶向下纯递归（指数级，仅对照）。"""
    if n == 0:
        return 0
    q = float("-inf")
    for i in range(1, n + 1):
        q = max(q, p[i] + cut_rod_naive(p, n - i))
    return q


def cut_rod_memo(p, n):
    """MEMOIZED-CUT-ROD：自顶向下 + 备忘。O(n²)"""
    memo = [-1] * (n + 1)
    memo[0] = 0

    def aux(k):
        if memo[k] >= 0:
            return memo[k]
        q = max(p[i] + aux(k - i) for i in range(1, k + 1)) if k else 0
        memo[k] = q
        return q

    return aux(n)


def cut_rod_bottom_up(p, n):
    """BOTTOM-UP-CUT-ROD。O(n²)"""
    r = [0] * (n + 1)
    for j in range(1, n + 1):
        q = float("-inf")
        for i in range(1, j + 1):
            q = max(q, p[i] + r[j - i])
        r[j] = q
    return r[n]


def cut_rod_with_plan(p, n):
    """EXTENDED-BOTTOM-UP：同时还原切割方案。返回 (最优值, 切割段列表)。"""
    r = [0] * (n + 1)
    s = [0] * (n + 1)
    for j in range(1, n + 1):
        q = float("-inf")
        for i in range(1, j + 1):
            if q < p[i] + r[j - i]:
                q = p[i] + r[j - i]
                s[j] = i
        r[j] = q
    cuts = []
    k = n
    while k > 0:
        cuts.append(s[k])
        k -= s[k]
    return r[n], cuts


def demo_rod():
    print("=" * 60)
    print("15.1 钢条切割（教科书 p=[0,1,5,8,9,10,17,17,20,24,30]，答案 r(10)=30）")
    p = [0, 1, 5, 8, 9, 10, 17, 17, 20, 24, 30]
    memo_hit = cut_rod_memo(p, 10)
    bottom = cut_rod_bottom_up(p, 10)
    naive = cut_rod_naive(p, 9)               # naive 10 会指数爆炸，9 做对照
    print(f"  r(10) memo={memo_hit} bottom-up={bottom}（教科书 30）", "✓" if memo_hit == bottom == 30 else "✗")
    print(f"  naive r(9)={naive}（教科书 25）", "✓" if naive == 25 else "✗")
    value, cuts = cut_rod_with_plan(p, 10)
    print(f"  最优切割方案: {cuts}（段长合计 = 10，最优值 {value}）",
          "✓" if sum(cuts) == 10 and value == 30 else "✗")
    # 规模对比：naive vs memo 的指数鸿沟
    prices = [0] + [random.Random(1).randrange(1, 50) for _ in range(30)]
    t0 = time.perf_counter()
    cut_rod_naive(prices, 22)
    t_naive = time.perf_counter() - t0
    t0 = time.perf_counter()
    cut_rod_memo(prices, 30)
    t_memo = time.perf_counter() - t0
    print(f"  n=22 naive: {t_naive*1000:8.1f} ms vs n=30 memo: {t_memo*1000:.2f} ms —— 指数 vs 多项式的鸿沟")


# ============================================================
# 15.2 矩阵链乘
# ============================================================
def matrix_chain_order(dims):
    """MATRIX-CHAIN-ORDER。dims = [p0,p1,...,pn]（n 个矩阵）。
    返回 (m, s)：m[i][j] 最少乘法次数，s 记录分割点。O(n³)"""
    n = len(dims) - 1
    m = [[0] * n for _ in range(n)]
    s = [[0] * n for _ in range(n)]
    for L in range(2, n + 1):                 # 链长
        for i in range(n - L + 1):
            j = i + L - 1
            m[i][j] = float("inf")
            for k in range(i, j):
                q = m[i][k] + m[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if q < m[i][j]:
                    m[i][j] = q
                    s[i][j] = k
    return m, s


def print_optimal_parens(s, i, j):
    """PRINT-OPTIMAL-PARENS。"""
    if i == j:
        return f"A{i+1}"
    return "(" + print_optimal_parens(s, i, s[i][j]) + print_optimal_parens(s, s[i][j] + 1, j) + ")"


def demo_matrix_chain():
    print("=" * 60)
    print("15.2 矩阵链乘（教科书 <A1·A2·A3·A4·A5·A6> 样例）")
    dims = [30, 35, 15, 5, 10, 20, 25]
    m, s = matrix_chain_order(dims)
    print(f"  dims={dims}")
    print(f"  最少乘法次数 m[1][6] = {m[0][5]}（教科书 15125）",
          "✓" if m[0][5] == 15125 else "✗")
    print(f"  最优括号化: {print_optimal_parens(s, 0, 5)}（教科书 ((A1(A2A3))((A4A5)A6))）")


# ============================================================
# 15.4 LCS
# ============================================================
def lcs(X, Y):
    """LCS-LENGTH + 方向表。O(mn)。返回 (长度, 序列)。"""
    m, n = len(X), len(Y)
    c = [[0] * (n + 1) for _ in range(m + 1)]
    b = [[None] * n for _ in range(m)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
                b[i - 1][j - 1] = "D"
            elif c[i - 1][j] >= c[i][j - 1]:
                c[i][j] = c[i - 1][j]
                b[i - 1][j - 1] = "U"
            else:
                c[i][j] = c[i][j - 1]
                b[i - 1][j - 1] = "L"
    # 回溯
    out = []
    i, j = m, n
    while i > 0 and j > 0:
        if b[i - 1][j - 1] == "D":
            out.append(X[i - 1])
            i -= 1
            j -= 1
        elif b[i - 1][j - 1] == "U":
            i -= 1
        else:
            j -= 1
    return c[m][n], "".join(reversed(out))


def demo_lcs():
    print("=" * 60)
    print("15.4 LCS（教科书 X=ABCBDAB, Y=BDCABA → LCS 长度 4）")
    X, Y = "ABCBDAB", "BDCABA"
    length, seq = lcs(X, Y)
    print(f"  LCS 长度 = {length}（教科书 4）", "✓" if length == 4 else "✗", f"| 序列之一: {seq}")
    # fuzz：随机串对拍「编辑距离风格」暴力校验（长度用另一 DP 实现复核）
    import itertools
    rng = random.Random(7)

    def lcs_len_ref(a, b):
        # 一维滚动数组复核实现
        prev = [0] * (len(b) + 1)
        for i in range(1, len(a) + 1):
            cur = [0] * (len(b) + 1)
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return prev[len(b)]

    bad = 0
    for _ in range(200):
        a = "".join(rng.choice("ABCD") for _ in range(rng.randrange(0, 15)))
        b = "".join(rng.choice("ABCD") for _ in range(rng.randrange(0, 15)))
        l1, _ = lcs(a, b)
        if l1 != lcs_len_ref(a, b):
            bad += 1
    print(f"  200 组随机串对拍（二维含回溯 vs 一维复核）:", "✓" if bad == 0 else f"✗ {bad}")


# ============================================================
# 15.4+ 0-1 背包
# ============================================================
def knapsack_01(weights, values, W):
    """0-1 背包：O(nW) 伪多项式。返回 (最大价值, 选择的物品)。"""
    n = len(weights)
    c = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            c[i][w] = c[i - 1][w]
            if weights[i - 1] <= w:
                cand = c[i - 1][w - weights[i - 1]] + values[i - 1]
                if cand > c[i][w]:
                    c[i][w] = cand
    # 回溯选了哪些
    chosen = []
    w = W
    for i in range(n, 0, -1):
        if c[i][w] != c[i - 1][w]:
            chosen.append(i - 1)
            w -= weights[i - 1]
    return c[n][W], sorted(chosen)


def demo_knapsack():
    print("=" * 60)
    print("0-1 背包（DP vs 暴力枚举对拍）")
    rng = random.Random(11)
    bad = 0
    for _ in range(60):
        n = rng.randrange(1, 14)
        W = rng.randrange(10, 60)
        ws = [rng.randrange(1, 15) for _ in range(n)]
        vs = [rng.randrange(1, 100) for _ in range(n)]
        # 暴力：枚举子集
        best = 0
        for mask in range(1 << n):
            tw = tv = 0
            for i in range(n):
                if mask >> i & 1:
                    tw += ws[i]
                    tv += vs[i]
                    if tw > W:
                        break
            else:
                best = max(best, tv)
        got, chosen = knapsack_01(ws, vs, W)
        # 校验所选物品合法且值一致
        tw = sum(ws[i] for i in chosen)
        tv = sum(vs[i] for i in chosen)
        if got != best or tw > W or tv != got:
            bad += 1
    print(f"  60 组随机对拍（DP vs 2^n 枚举）:", "✓" if bad == 0 else f"✗ {bad}")
    n = 24
    W = 100
    ws = [rng.randrange(1, 20) for _ in range(n)]
    vs = [rng.randrange(1, 100) for _ in range(n)]
    t0 = time.perf_counter()
    knapsack_01(ws, vs, W)
    t_dp = time.perf_counter() - t0
    print(f"  DP n=24 W=100: {t_dp*1000:.1f} ms（暴力 2^24 组合约需数十秒——DP 的存在意义）")


# ============================================================
# 应用：git diff 的本质（LCS）
# ============================================================
def demo_diff():
    print("=" * 60)
    print("应用：文本 diff —— LCS 的工业实现（git diff 本质）")
    old_lines = [
        "def calc(a, b):",
        "    total = a + b",
        "    print(total)",
        "    return total",
        "",
        "if __name__ == '__main__':",
        "    calc(1, 2)",
    ]
    new_lines = [
        "def calc(a, b, scale=1):",
        "    total = (a + b) * scale",
        "    print(total)",
        "    return total",
        "",
        "if __name__ == '__main__':",
        "    x = calc(1, 2)",
        "    print(x)",
    ]
    # 对行做 LCS：old 行加哨兵保证可比较重复行（教科书处理：带行号标 (i,j) 使唯一）
    X = [(l, i) for i, l in enumerate(old_lines)]          # 加行号使重复行可辨识
    Y = [(l, j) for j, l in enumerate(new_lines)]
    # 用 dict 加速的 LCS（行号内嵌已保证唯一性的对比较）
    def lcs_pairs(X, Y):
        m, n = len(X), len(Y)
        c = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i - 1][0] == Y[j - 1][0]:            # 只比较行文本，行号用于回溯
                    c[i][j] = c[i - 1][j - 1] + 1
                else:
                    c[i][j] = max(c[i - 1][j], c[i][j - 1])
        i, j = m, n
        pairs = []
        while i > 0 and j > 0:
            if X[i - 1][0] == Y[j - 1][0] and c[i][j] == c[i - 1][j - 1] + 1:
                pairs.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif c[i - 1][j] >= c[i][j - 1]:
                i -= 1
            else:
                j -= 1
        return list(reversed(pairs))

    pairs = lcs_pairs(X, Y)
    # 按 LCS 对齐生成 diff：未匹配的 old 行 = 删，未匹配的 new 行 = 增
    oi = fj = 0
    diff = []
    for i, j in pairs + [(len(old_lines), len(new_lines))]:
        while oi < i:
            diff.append(f"  - {old_lines[oi]}")
            oi += 1
        while fj < j:
            diff.append(f"  + {new_lines[fj]}")
            fj += 1
        if i < len(old_lines):
            diff.append(f"    {old_lines[i]}")
            oi, fj = i + 1, j + 1
    for line in diff:
        print(line)
    print("  → 「公共行」由 LCS 对齐，其余标 + / -，就是 git diff 的骨架；")
    print("    真实 git 还会做行内细化（Myers 算法 + 启发式），但骨架就是 15.4。")


def main():
    demo_rod()
    demo_matrix_chain()
    demo_lcs()
    demo_knapsack()
    demo_diff()


if __name__ == "__main__":
    main()
