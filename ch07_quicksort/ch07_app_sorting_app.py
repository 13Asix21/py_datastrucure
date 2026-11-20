# -*- coding: utf-8 -*-
"""
ch7-9 排序应用：排序的三个工业现场
《算法导论（原书第3版）》CLRS ch7-9

  1) 数据库 ORDER BY：多列稳定排序（快排不稳定，工程通用快排都是 introsort+稳定合并收尾）
     → 演示 Python sorted 的稳定性 + 自己实现稳定合并
  2) 大文件外排（external merge sort 思路）：内存装不下时的 K 路归并
     → 归并排序实践 + heapq.merge
  3) Top-N 热榜：快排选 vs 全排 vs 堆——ch9/ch6 的联合应用
"""

import os
import sys
import heapq
import random
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from ch06_heaps.ch06_01_heap import MaxHeap
from ch09_selection.ch09_selection import select_bfprt


# ============================================================
# 1) 多列稳定排序（数据库 ORDER BY 语义）
# ============================================================
def merge_sort_stable(pairs):
    """自合并排序：稳定 O(n lg n)。演示稳定性的载体。"""
    if len(pairs) <= 1:
        return list(pairs)
    mid = len(pairs) // 2
    left = merge_sort_stable(pairs[:mid])
    right = merge_sort_stable(pairs[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][0] <= right[j][0]:            # ≤ = 相等取左 → 稳定
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def demo_multicolumn():
    print("=" * 60)
    print("应用1：ORDER BY 语义——级联排序必须用稳定排序")
    rnd = random.Random(5)
    rows = [(rnd.choice("WXYZ"), rnd.randrange(0, 5)) for _ in range(300)]
    def msort(pairs, key):
        # 带键的稳定合并（模拟 sorted(key=...)）
        if len(pairs) <= 1:
            return list(pairs)
        mid = len(pairs) // 2
        left = msort(pairs[:mid], key); right = msort(pairs[mid:], key)
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if key(left[i]) <= key(right[j]):
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
        out.extend(left[i:]); out.extend(right[j:])
        return out
    cascade = msort(rows, lambda r: r[1])                # 先 score
    cascade = msort(cascade, lambda r: r[0])             # 再 name（稳定 → score 次序在同名内保留）
    # 参照：Python sorted 元组键
    reference = sorted(rows, key=lambda r: (r[0], r[1]))
    ok = cascade == reference
    print(f"  300 行 (name, score)：级联稳定排序 == sorted((name,score)) 元组键:", "✓" if ok else "✗")
    # 反面教材：快排不稳定（教科书 7 章注脚）
    from ch07_quicksort import quicksort_lomuto
    arr = [(rnd.choice("AB"), i) for i in range(100)]     # 同键 A/B 但带原序号
    qs = quicksort_lomuto(list(arr))
    def is_stable(result):
        for k in ("A", "B"):
            idxs = [r[1] for r in result if r[0] == k]
            if idxs != sorted(idxs):                    # 同键内原序号必须保序
                return False
        return True
    unstable = not is_stable(qs)
    print(f"  快排对含等键数据: {'实测破坏相对次序 ✓（原址快排不稳定，数据库引擎用稳定归并收尾的原因）' if unstable else '本批偶然保序（不稳定排序不保证，数据相关）'}")


# ============================================================
# 2) 外排：K 路归并（大文件排序的骨架）
# ============================================================
def demo_external_merge():
    print("=" * 60)
    print("应用2：外排思想——3 万条记录分 30 个已排序块，K 路归并合并")
    random.seed(9)
    N, CHUNK = 30_000, 1000
    data = [random.randrange(1_000_000) for _ in range(N)]
    # 生成已排序块（模拟"内存排序各自块"后的落盘）
    runs = []
    for i in range(0, N, CHUNK):
        runs.append(sorted(data[i:i + CHUNK]))
    # K 路归并：heapq.merge（本质是 K 路小顶堆比较头元素——归并树）
    t0 = time.perf_counter()
    merged = list(heapq.merge(*runs))
    t_merge = time.perf_counter() - t0
    ok = merged == sorted(data)
    print(f"  30 个块合并 {N} 条: {'✓ 与全量排序一致' if ok else '✗'} | K路归并 {t_merge*1000:.1f} ms")
    # 对照：全量重排（真外排里内存装不下时做不到）
    t0 = time.perf_counter()
    sorted(data)
    t_full = time.perf_counter() - t0
    print(f"  对照全量 sorted: {t_full*1000:.1f} ms")
    print("  读数：外排 = 分块内排 + 多轮 K 路归并，I/O 代价 = 块数×2 次读写；")
    print("        heapq.merge 的比较动作只发生在各块头部 → 单趟 O(N lg K)，K=块数远小于 N。")


# ============================================================
# 3) Top-N 热榜：三种选法的对比
# ============================================================
def demo_topn():
    print("=" * 60)
    print("应用3：Top-N 热榜三解法（N=20 万条流，取 Top 10）")
    n, k = 200_000, 10
    stream = [random.randrange(1_000_000) for _ in range(n)]
    # A) 全量排序取头
    t0 = time.perf_counter()
    a = sorted(stream, reverse=True)[:k]
    t_a = time.perf_counter() - t0
    # B) nlargest（内部为小顶堆守门员，C 实现）
    t0 = time.perf_counter()
    b = heapq.nlargest(k, stream)
    t_b = time.perf_counter() - t0
    # C) SELECT 定位第 k 大 + 过滤扫描（并列截断：严格大于 threshold 的全收，缺额用 threshold 补齐）
    t0 = time.perf_counter()
    arr = list(stream)
    kth_desc = select_bfprt(arr, len(arr) - k + 1)        # 升序第 (n-k+1) 位 = 降序第 k 位
    above = sorted([x for x in arr if x > kth_desc], reverse=True)
    need = k - len(above)
    c = above + [kth_desc] * need                          # 并列边界按补齐语义截断
    t_c = time.perf_counter() - t0
    ok = a == b == c
    print(f"  三方结果一致: {'✓' if ok else '✗'}（并列边界按截断语义处理，各方对第 k 位取值一致）")
    print(f"  全量 sorted+切片: {t_a*1000:8.1f} ms | heapq.nlargest: {t_b*1000:7.1f} ms | SELECT+过滤: {t_c*1000:7.1f} ms")
    print("  读数：nlargest 是 O(n lg k) 的 C 实现，工程默认解；SELECT 数学最优 O(n)（选 k 大本身线性）")
    print("        但构造 Top 列表还需 lg k 排序尾部 → 工程上 nlargest 常数更香，数学题 SELECT 封王。")


def main():
    demo_multicolumn()
    demo_external_merge()
    demo_topn()


if __name__ == "__main__":
    main()
