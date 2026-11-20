# -*- coding: utf-8 -*-
"""
第7章 快速排序 —— 7.1~7.3 Lomuto / 随机化 / Hoare 三版本
《算法导论（原书第3版）》CLRS ch7

QUICKSORT：分治。期望 O(n lg n)，最坏 O(n²)（已排序输入 + 固定主元）。
  7.1  Lomuto 分区（教科书主版本，尾部单点扫描）
  7.2  随机化快排： RANDOM-SAMPLE 主元，期望保证
  7.3  Hoare 分区（双指针，练习对照；作者原版分区）
对拍：三版本 vs sorted；已排序输入退化实验；比较计数对比。
"""

import random
import time


# ============================================================
# 7.1 Lomuto 分区版（教科书 pseudocode 7.1）
# ============================================================
def partition_lomuto(A, p, r, counter=None):
    """PARTITION(A, p, r)：A[r] 为主元，返回最终下标。"""
    x = A[r]                                  # 主元
    i = p - 1
    for j in range(p, r):
        if counter is not None:
            counter[0] += 1
        if A[j] <= x:
            i += 1
            A[i], A[j] = A[j], A[i]
    A[i + 1], A[r] = A[r], A[i + 1]
    return i + 1


def quicksort_lomuto(A, p=0, r=None, counter=None):
    """QUICKSORT。原地。"""
    if r is None:
        r = len(A) - 1
    if p < r:
        q = partition_lomuto(A, p, r, counter)
        quicksort_lomuto(A, p, q - 1, counter)
        quicksort_lomuto(A, q + 1, r, counter)
    return A


# ============================================================
# 7.2 随机化版
# ============================================================
def partition_random(A, p, r, rng, counter=None):
    """RANDOMIZED-PARTITION：随机选主元与尾部交换再走 Lomuto。"""
    i = rng.randrange(p, r + 1)
    A[r], A[i] = A[i], A[r]
    return partition_lomuto(A, p, r, counter)


def quicksort_random(A, p=0, r=None, rng=None, counter=None):
    if rng is None:
        rng = random
    if r is None:
        r = len(A) - 1
    if p < r:
        q = partition_random(A, p, r, rng, counter)
        quicksort_random(A, p, q - 1, rng, counter)
        quicksort_random(A, q + 1, r, rng, counter)
    return A


# ============================================================
# 7.3 Hoare 分区（教科书练习 7.1，原 1961 版）
# ============================================================
def partition_hoare(A, p, r, counter=None):
    """HOARE-PARTITION：双指针从两端相向收紧。"""
    x = A[p]
    i = p - 1
    j = r + 1
    while True:
        while True:
            j -= 1
            if counter is not None:
                counter[0] += 1
            if A[j] <= x:
                break
        while True:
            i += 1
            if counter is not None:
                counter[0] += 1
            if A[i] >= x:
                break
        if i < j:
            A[i], A[j] = A[j], A[i]
        else:
            return j


def quicksort_hoare(A, p=0, r=None, counter=None):
    """Hoare 分区的递归（分区点处理与 Lomuto 不同：两侧都含分区点）。"""
    if r is None:
        r = len(A) - 1
    if p < r:
        q = partition_hoare(A, p, r, counter)
        quicksort_hoare(A, p, q, counter)          # 注意：不排除 q
        quicksort_hoare(A, q + 1, r, counter)
    return A


# ============================================================
# 尾递归优化版（思考题 7-4 的工程化：QUICKSORT'）
# ============================================================
def quicksort_tail(A, rng=None, counter=None):
    """消除一侧重递归：while 循环吃掉大的那半，栈深 O(lg n)。
    Python 无真尾调用，但循环版确实把最坏栈深砍到 O(lg n)。"""
    if rng is None:
        rng = random
    p, r = 0, len(A) - 1
    stack = 0
    while p < r:
        q = partition_random(A, p, r, rng, counter)
        # 只递归小的一半，另一半用循环续处理
        if q - p < r - q:
            quicksort_tail_recur(A, p, q - 1, rng, counter, stack + 1)
            p = q + 1
        else:
            quicksort_tail_recur(A, q + 1, r, rng, counter, stack + 1)
            r = q - 1
    return A


def quicksort_tail_recur(A, p, r, rng, counter, depth):
    while p < r:
        q = partition_random(A, p, r, rng, counter)
        if q - p < r - q:
            quicksort_tail_recur(A, p, q - 1, rng, counter, depth + 1)
            p = q + 1
        else:
            quicksort_tail_recur(A, q + 1, r, rng, counter, depth + 1)
            r = q - 1


# ============================================================
# demo
# ============================================================
def demo_correctness():
    print("=" * 60)
    print("7.1~7.3 三版本正确性 fuzz（150 组随机 + 边界）")
    random.seed(42)
    bad = 0
    cases = [
        [], [1], [2, 1], [1, 2], [5, 5, 5, 5],
        list(range(20)), list(range(20, 0, -1)),
    ]
    for _ in range(150):
        n = random.randrange(0, 60)
        cases.append([random.randrange(-100, 100) for _ in range(n)])
    for arr in cases:
        expect = sorted(arr)
        for name, fn in [
            ("Lomuto", lambda a: quicksort_lomuto(list(a))),
            ("Random", lambda a: quicksort_random(list(a))),
            ("Hoare", lambda a: quicksort_hoare(list(a))),
            ("TailElim", lambda a: quicksort_tail(list(a))),
        ]:
            got = fn(arr)
            if got != expect:
                bad += 1
                if bad <= 2:
                    print(f"  ✗ {name} on {arr[:10]}...: {got[:10]}...")
    print(f"  {len(cases)} 组 × 4 版本:", "✓ 全部一致" if bad == 0 else f"✗ {bad} 次失败")


def demo_worst_case():
    print("=" * 60)
    print("7.2 最坏 vs 期望：已排序输入的比较次数（n=300）")
    n = 300
    sorted_input = list(range(n))
    # Lomuto 固定取尾 → 已排序输入退化 O(n²)
    c_fixed = [0]
    quicksort_lomuto(list(sorted_input), counter=c_fixed)
    # 随机化 → 期望 ~2n ln n
    rng = random.Random(7)
    c_rand = [0]
    quicksort_random(list(sorted_input), rng=rng, counter=c_rand)
    import math
    expect_bound = 2 * n * math.log(n)
    print(f"  固定主元（Lomuto）: {c_fixed[0]:6d} 次比较 ≈ n²/2 = {n*n//2}")
    print(f"  随机主元         : {c_rand[0]:6d} 次比较 vs 期望上界 2n·ln n ≈ {expect_bound:.0f}")
    print(f"  → 随机化把最坏 n² 压回期望 n lg n：{c_fixed[0]/c_rand[0]:.1f}× 差距；单次随机实验在界附近属正常")


def demo_bench():
    print("=" * 60)
    print("效率：随机数据 n=20000（纯 Python 实现）")
    random.seed(11)
    arr = [random.randrange(1_000_000) for _ in range(20_000)]
    variants = [
        ("Lomuto", lambda a: quicksort_lomuto(list(a))),
        ("Hoare", lambda a: quicksort_hoare(list(a))),
        ("Random", lambda a: quicksort_random(list(a))),
        ("Python sorted(Timsort)", lambda a: sorted(a)),
    ]
    base = list(arr)
    for name, fn in variants:
        t0 = time.perf_counter()
        out = fn(base)
        dt = time.perf_counter() - t0
        ok = out == sorted(base)
        print(f"  {name:<22} {dt*1000:8.1f} ms  {'✓' if ok else '✗'}")
    print("  读数：Hoare 平均交换更少通常更快；Timsort 是 C 实现不在一个量级。")
    print("        快排的工程地位来自原址+缓存友好，纯快排对竞品在全量重排上仍站得住。")


def main():
    demo_correctness()
    demo_worst_case()
    demo_bench()


if __name__ == "__main__":
    main()
