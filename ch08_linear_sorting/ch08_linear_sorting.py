# -*- coding: utf-8 -*-
"""
第8章 线性时间排序 —— 8.1~8.4 计数 / 基数 / 桶
《算法导论（原书第3版）》CLRS ch8

下界（8.1）：比较排序最坏 Ω(n lg n)——决策树论证。
突破下界的方法：不比较，用值域信息。
  8.2 计数排序 COUNTING-SORT：k=值域，O(n+k)，稳定
  8.3 基数排序 RADIX-SORT：按位多轮计数排序，O(d(n+k))
  8.4 桶排序 BUCKET-SORT：均匀分布假设，期望 O(n)

对拍 sorted + 适用域实验（值域/分布敏感性）。
"""

import random
import time


# ============================================================
# 8.2 计数排序
# ============================================================
def counting_sort(A, k=None):
    """COUNTING-SORT。A ∈ [0, k]。O(n+k)，稳定（教科书先数 C 再累计再倒序回填）。"""
    if not A:
        return []
    if k is None:
        k = max(A)
    C = [0] * (k + 1)
    for a in A:
        C[a] += 1
    for i in range(1, k + 1):
        C[i] += C[i - 1]
    B = [None] * len(A)
    for j in range(len(A) - 1, -1, -1):        # 倒序 = 保持稳定
        B[C[A[j]] - 1] = A[j]
        C[A[j]] -= 1
    return B


# ============================================================
# 8.3 基数排序
# ============================================================
def radix_sort(A, d=None):
    """RADIX-SORT：n 个 d 位十进制数（或 k 进制位）。
    每轮调用稳定排序（这里用计数排序按位）。O(d(n+k))。"""
    if not A:
        return []
    if d is None:
        d = len(str(max(A)))
    for exp in range(d):
        base = 10 ** exp
        # 按当前位计数排序
        digits = [(a // base) % 10 for a in A]
        k = 9
        C = [0] * (k + 1)
        for dg in digits:
            C[dg] += 1
        for i in range(1, k + 1):
            C[i] += C[i - 1]
        B = [None] * len(A)
        for j in range(len(A) - 1, -1, -1):
            B[C[digits[j]] - 1] = A[j]
            C[digits[j]] -= 1
        A = B
    return A


# ============================================================
# 8.4 桶排序
# ============================================================
def bucket_sort(A):
    """BUCKET-SORT：输入均匀分布于 [0,1)。期望 O(n)。
    n 个桶 + 桶内插入排序 + 依次连接。"""
    n = len(A)
    if n == 0:
        return []
    buckets = [[] for _ in range(n)]
    for a in A:
        buckets[min(int(n * a), n - 1)].append(a)
    out = []
    for b in buckets:
        _insertion_sort(b)
        out.extend(b)
    return out


def _insertion_sort(a):
    """插排（桶内小数据，教科书原配）。"""
    for j in range(1, len(a)):
        key = a[j]
        i = j - 1
        while i >= 0 and a[i] > key:
            a[i + 1] = a[i]
            i -= 1
        a[i + 1] = key


# ============================================================
# demo
# ============================================================
def demo_correctness():
    print("=" * 60)
    print("8.2~8.4 三种线性排序正确性 fuzz")
    random.seed(3)
    bad = 0
    # 计数排序：非负小值域
    for _ in range(80):
        arr = [random.randrange(0, 200) for _ in range(random.randrange(0, 100))]
        if counting_sort(arr) != sorted(arr):
            bad += 1
    print("  计数排序  80 组随机（值域 0..199）:", "✓" if bad == 0 else f"✗ {bad}")
    # 基数排序：非负整数
    bad = 0
    for _ in range(80):
        arr = [random.randrange(0, 10 ** random.randrange(1, 7)) for _ in range(random.randrange(0, 100))]
        if radix_sort(list(arr)) != sorted(arr):
            bad += 1
    print("  基数排序  80 组随机（1~6 位十进制）:", "✓" if bad == 0 else f"✗ {bad}")
    # 桶排序：[0,1) 浮点
    bad = 0
    for _ in range(80):
        arr = [random.random() for _ in range(random.randrange(0, 100))]
        if bucket_sort(arr) != sorted(arr):
            bad += 1
    print("  桶排序    80 组随机（均匀 [0,1)）  :", "✓" if bad == 0 else f"✗ {bad}")


def demo_lower_bound_talk():
    print("=" * 60)
    print("8.1 为什么比较排序快不过 n·lg n（决策树论证）")
    import math
    for n in (10, 100, 1000, 1_000_000):
        leaves = math.factorial(n) if n <= 100 else None
        lb = math.ceil(math.log2(math.factorial(n))) if n <= 170 else None
        if lb is None:
            # Stirling 近似
            lb = math.ceil(n * math.log2(n) - n * math.log2(math.e))
        print(f"  n={n:>8}: n! 种排列 → 树高 ≥ lg(n!) ≈ {lb:>12} ≈ n·lg n = {n*math.log2(n):,.0f}")


def demo_adaptivity():
    print("=" * 60)
    print("适用域实验：值域 k 对计数排序 / 分布对桶排序的影响")
    random.seed(9)
    n = 20_000
    # 值域扫描：计数排序 O(n+k)
    for k in (1_000, 100_000, 5_000_000):
        arr = [random.randrange(k) for _ in range(n)]
        t0 = time.perf_counter()
        counting_sort(arr, k=k - 1)
        t_cs = time.perf_counter() - t0
        t0 = time.perf_counter()
        sorted(arr)
        t_py = time.perf_counter() - t0
        ratio = f"{t_py/t_cs:.1f}×" if t_cs < t_py else f"1/{t_cs/t_py:.1f}"
        print(f"  计数排序 n={n}, k={k:>8}: {t_cs*1000:7.1f} ms | Python sorted {t_py*1000:6.1f} ms → {'计数快 ' + ratio if t_cs < t_py else 'sorted 快 ' + ratio}")
    # 分布敏感性：均匀 vs 集中
    uniform = [random.random() for _ in range(n)]
    skewed = [min(random.random(), random.random()) for _ in range(n)]    # 偏 0 端
    t0 = time.perf_counter(); bucket_sort(list(uniform)); t_u = time.perf_counter() - t0
    t0 = time.perf_counter(); bucket_sort(list(skewed)); t_s = time.perf_counter() - t0
    print(f"  桶排序 n={n}: 均匀输入 {t_u*1000:.1f} ms vs 集中输入 {t_s*1000:.1f} ms")
    print("  读数：①计数排序 O(n+k)：k ≫ n 时数组比元素还多，k=500 万时慢 143 倍——")
    print("          值域可控（成绩/年龄/枚举）才是它的主场（数据库基数排序/GPU 排序内核）。")
    print("        ②桶排序本例偏斜得不狠（min(min,..) 只把密度推向低端，多数桶仍短），")
    print("          若集中到个位数桶内插排会退化 O(n²)——期望 O(n) 押的是「均匀」二字。")


def main():
    demo_correctness()
    demo_lower_bound_talk()
    demo_adaptivity()


if __name__ == "__main__":
    main()
