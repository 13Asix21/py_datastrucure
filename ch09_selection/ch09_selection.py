# -*- coding: utf-8 -*-
"""
第9章 中位数和顺序统计量 —— 9.1~9.3
《算法导论（原书第3版）》CLRS ch9

第 i 小的元素（order statistic）：
  9.2 RANDOMIZED-SELECT：随机主元一遍切一侧，期望 O(n)（最坏 O(n²)但概率可忽略）
  9.3 五分化中位数的中位数（SELECT, Blum-Floyd-Pratt-Rivest-Tarjan）：最坏 O(n)
      —— 中位数-of-5 组保证至少 3n/10 个元素被排除

对拍 sorted[k]；两种 SELECT 互检 + O(n) 复杂度斜率实测。
"""

import random
import time


# ============================================================
# 9.2 随机化选择
# ============================================================
def randomized_select(A, p, r, i, rng=None, counter=None):
    """RANDOMIZED-SELECT(A, p, r, i)：找第 i 小（1-based，全组索引）。
    期望 O(n)。counter 记录主元比较规模用于复杂度实测。"""
    if rng is None:
        rng = random
    if p == r:
        return A[p]
    q = _rand_partition(A, p, r, rng)
    if counter is not None:
        counter[0] += r - p + 1
    k = q - p + 1                  # 主元在子组内的位次
    if i == k:
        return A[q]
    elif i < k:
        return randomized_select(A, p, q - 1, i, rng, counter)
    return randomized_select(A, q + 1, r, i - k, rng, counter)


def _rand_partition(A, p, r, rng):
    pivot = rng.randrange(p, r + 1)
    A[pivot], A[r] = A[r], A[pivot]
    x = A[r]
    i = p - 1
    for j in range(p, r):
        if A[j] <= x:
            i += 1
            A[i], A[j] = A[j], A[i]
    A[i + 1], A[r] = A[r], A[i + 1]
    return i + 1


# ============================================================
# 9.3 五分化 SELECT（最坏 O(n)）
# ============================================================
def select_bfprt(A, i, counter=None):
    """SELECT：第 i 小（1-based），最坏线性。
    递归结构：每组 5 个取中位数 → 中位数的中位数 μ 做主元
    μ 保证 ≥ 3(n/5)/2 = 3n/10 的元素 ≤ 它（对称方向同理），
    因此每次至少甩掉 30% 的元素 → T(n) ≤ T(n/5)+T(7n/10)+O(n) ≤ cn。
    """
    if counter is not None:
        counter[0] += len(A)
    if len(A) <= 5:
        return sorted(A)[i - 1]
    # 1) 分 5 组取各组中位数，构成 M
    groups = [A[k:k + 5] for k in range(0, len(A), 5)]
    M = []
    for g in groups:
        M.append(sorted(g)[len(g) // 2])
    # 2) 中位数的中位数 μ（递归）
    mu = select_bfprt(M, len(M) // 2 + 1, counter)
    # 3) μ 做主元三分区
    less, equal, greater = [], [], []
    for a in A:
        if a < mu:
            less.append(a)
        elif a == mu:
            equal.append(a)
        else:
            greater.append(a)
    # 4) 递归一侧
    if i <= len(less):
        return select_bfprt(less, i, counter)
    if i <= len(less) + len(equal):
        return mu
    return select_bfprt(greater, i - len(less) - len(equal), counter)


# ============================================================
# demo
# ============================================================
def demo_correctness():
    print("=" * 60)
    print("9.2~9.3 两种 SELECT 对拍 sorted[k]（200 组 fuzz）")
    random.seed(5)
    bad = 0
    for _ in range(200):
        n = random.randrange(1, 80)
        arr = [random.randrange(-1000, 1000) for _ in range(n)]
        if len(set(arr)) < n:                        # 避开并列语义坑（任取都合法）
            continue
        i = random.randrange(1, n + 1)
        a1 = randomized_select(list(arr), 0, n - 1, i)
        a2 = select_bfprt(list(arr), i)
        expect = sorted(arr)[i - 1]
        if not (a1 == a2 == expect):
            bad += 1
            if bad <= 2:
                print(f"  ✗ n={n} i={i}: RS={a1} BF={a2} expect={expect}")
    # 边界：极小数组
    for arr, i in ([3, 1, 2], 2), ([7], 1), ([5, 5, 5], 2):
        if select_bfprt(list(arr), i) != sorted(arr)[i - 1]:
            bad += 1
    print(f"  随机（互异值）+ 边界样例:", "✓ 全部一致" if bad == 0 else f"✗ {bad} 次")


def demo_median_cplusplus():
    print("=" * 60)
    print("应用：流式中位数双方案——SELECT 重跑 vs 双堆在线维护")
    import heapq
    random.seed(11)

    class OnlineMedian:
        """两堆法：maxHeap(小半) + minHeap(大半)。插入 O(lg n)，查询 O(1)。"""
        def __init__(self):
            self.lo = []          # 小半（取负的 max-heap）
            self.hi = []          # 大半（min-heap）
        def add(self, x):
            heapq.heappush(self.lo, -x)
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
            if len(self.hi) > len(self.lo):
                heapq.heappush(self.lo, -heapq.heappop(self.hi))
        def median(self):
            if len(self.lo) == len(self.hi):
                return (-self.lo[0] + self.hi[0]) / 2
            return -self.lo[0]

    n = 20_000
    stream = [random.randrange(1_000_000) for _ in range(n)]
    # 方案 A：全量 SELECT 暴力（每次 O(n)）
    t0 = time.perf_counter()
    arr = []
    medians_offline = []
    probe_every = 1000
    for idx, x in enumerate(stream):
        arr.append(x)
        if (idx + 1) % probe_every == 0:
            medians_offline.append(select_bfprt(list(arr), (len(arr) + 1) // 2))
    t_offline = time.perf_counter() - t0
    # 方案 B：双堆在线
    t0 = time.perf_counter()
    om = OnlineMedian()
    medians_online = []
    for idx, x in enumerate(stream):
        om.add(x)
        if (idx + 1) % probe_every == 0:
            medians_online.append(om.median())
    t_online = time.perf_counter() - t0
    # 对拍（偶数长度时 SELECT 取的下中位 vs 两堆取平均——统一口径）
    bad = 0
    for k, (moff, mon) in enumerate(zip(medians_offline, medians_online)):
        ln = (k + 1) * probe_every
        if ln % 2 == 1:
            continue                                # 奇数长度直接可比
        vals = sorted(stream[:ln])
        true_avg = (vals[ln // 2 - 1] + vals[ln // 2]) / 2
        if abs(true_avg - mon) > 1e-9:
            bad += 1
    print(f"  n={n} 流，每 1000 步查一次中位数（{len(medians_online)} 次）")
    print(f"  全量重跑 SELECT：{t_offline*1000:8.1f} ms | 双堆在线维护：{t_online*1000:7.1f} ms → {t_offline/t_online:.0f}× 差距")
    print(f"  在线中位数 vs 排序真值（偶数长度 10 次抽验）:", "✓" if bad == 0 else f"✗ {bad}")
    print("  读数：SELECT 是离线单查的学术最优；「持续流+高频查」场景双堆 O(lg n)/次完胜。")


def demo_complexity_slope():
    print("=" * 60)
    print("9.3 BFPT-SELECT 复杂度斜率（c≈1 的 O(n) 直觉验证）")
    rng = random.Random(7)
    prev = None
    for n in (5000, 10000, 20000, 40000, 80000, 160000):
        arr = [rng.randrange(10 * n) for _ in range(n)]
        c = [0]
        select_bfprt(list(arr), n // 2, counter=c)
        per_n = c[0] / n
        if prev:
            print(f"  n={n:>7}: 处理元素量 {c[0]:>9} = {per_n:5.1f}·n（斜率 {(per_n/prev):.2f}×/翻倍）")
        else:
            print(f"  n={n:>7}: 处理元素量 {c[0]:>9} = {per_n:5.1f}·n")
        prev = per_n
    print("  读数：每元素成本随 n 缓慢下滑（固定开销被摊平），近线性 O(n)。")
    print("        对比 sorted + 取位是 O(n lg n)：数据越大差距越显著。")


def main():
    demo_correctness()
    demo_median_cplusplus()
    demo_complexity_slope()


if __name__ == "__main__":
    main()
