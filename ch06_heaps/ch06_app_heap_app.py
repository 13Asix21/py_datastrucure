# -*- coding: utf-8 -*-
"""
第6章 应用：堆的三个实战面孔
《算法导论（原书第3版）》CLRS ch6

  1) Top-K：数据流前 K 大元素（热搜榜/限流榜单内核）
     小顶堆 keeper vs 全量排序 vs heapq.nlargest 三方对拍 + 计时
  2) 任务调度： deadlines 优先队列（操作系统/中间件的任务内核）
     MaxHeap vs heapq 同场景对拍
  3) 就地堆排序 vs Python 内置 sorted 的规模扫描
"""

import os
import sys
import time
import random
import heapq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch06_01_heap import MaxHeap


# ============================================================
# 1) Top-K（用最小堆当"门槛"：堆顶是第 K 大的守门员）
# ============================================================
class TopKKeeper:
    """数据流 Top-K：维护容量 K 的小顶堆。"""
    def __init__(self, k):
        self.k = k
        self.h = []                        # 小顶堆（heapq 原生语义）

    def feed(self, x):
        if len(self.h) < self.k:
            heapq.heappush(self.h, x)
        elif x > self.h[0]:                # 挤掉守门员
            heapq.heapreplace(self.h, x)

    def topk(self):
        return sorted(self.h, reverse=True)


class TopKOurHeap:
    """同语义，用 ch6 MaxHeap 镜像实现：key 取负，堆顶 = 守门员(第 K 大的负值)。"""
    def __init__(self, k):
        self.k = k
        self.h = MaxHeap()

    def feed(self, x):
        if len(self.h) < self.k:
            self.h.insert(-x)               # 容量未满：直接进
        elif x > -self.h.maximum():          # 超过守门员：挤掉再进
            self.h.extract_max()
            self.h.insert(-x)

    def topk(self):
        out = []
        while len(self.h):
            out.append(-self.h.extract_max())
        return sorted(out, reverse=True)    # 堆被清空，适合终点一次性榜单


def demo_topk():
    print("=" * 60)
    print("应用1：Top-K（K=10，数据流 10 万元素）")
    random.seed(5)
    n = 100_000
    stream = [random.randrange(1_000_000) for _ in range(n)]
    k = 10
    # 三方对拍
    a = TopKKeeper(k)
    for x in stream:
        a.feed(x)
    l1 = a.topk()
    b = TopKOurHeap(k)
    for x in stream:
        b.feed(x)
    l2 = b.topk()
    l3 = heapq.nlargest(k, stream)
    l4 = sorted(stream, reverse=True)[:k]
    # 四方值对拍（随机 key 互异，应逐位一致）
    ok = l1 == l2 == l3 == l4
    print(f"  四方对拍（守门员×2 / nlargest / 全排序）: {'✓ 全一致' if ok else '✗'}  Top3 = {l1[:3]}")
    # 计时
    t0 = time.perf_counter()
    a2 = TopKKeeper(k)
    # 守门员版直接 heapq O(n lg k)：
    for x in stream:
        a2.feed(x)
    t_keeper = time.perf_counter() - t0
    t0 = time.perf_counter()
    for x in stream:
        pass
    _ = sorted(stream, reverse=True)[:k]
    t_sort = time.perf_counter() - t0
    t0 = time.perf_counter()
    heapq.nlargest(k, stream)
    t_nl = time.perf_counter() - t0
    print(f"  堆守门员 O(n lg k): {t_keeper*1000:7.1f} ms | 全排序 O(n lg n): {t_sort*1000:7.1f} ms | heapq.nlargest: {t_nl*1000:6.2f} ms")
    print(f"  → 海量流式场景只存 K 个元素：内存 O(k)，免去 O(n) 排序。")


# ============================================================
# 2) 任务调度：按优先级弹出（deadline 语义）
# ============================================================
class Task:
    __slots__ = ("name", "priority")

    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def __repr__(self):
        return f"{self.name}(p={self.priority})"


class TaskScheduler:
    """ch6 MaxHeap 驱动的任务队列。"""
    def __init__(self):
        self.h = MaxHeap()

    def submit(self, name, priority):
        # 元组比较：priority 先比。占位哨兵用同类型 (-1, "") 保可比性
        self.h.insert((priority, name), neg_inf=(-1, ""))

    def run_next(self):
        if not len(self.h):
            return None
        p, name = self.h.extract_max()
        return name


def demo_scheduler():
    print("=" * 60)
    print("应用2：任务调度器（10 万任务提交+全弹出）")
    random.seed(7)
    tasks = [(f"job{i}", random.randrange(1_000_000)) for i in range(100_000)]
    # 正确性：我们的 MaxHeap vs heapq
    # 注：同优先级并列时弹出顺序不定（两者都是合法堆语义），
    #     对拍判据 = 弹出的"优先级序列"逐位一致，而非名字序列。
    sch = TaskScheduler()
    hp_ref = []
    for name, p in tasks:
        sch.submit(name, p)
        heapq.heappush(hp_ref, (-p, name))
    pri_ours = []
    for _ in range(len(tasks)):
        p, name = sch.h.extract_max()
        pri_ours.append(p)
    pri_ref = []
    while hp_ref:
        negp, name = heapq.heappop(hp_ref)
        pri_ref.append(-negp)
    ok = pri_ours == pri_ref
    print(f"  10 万任务弹出优先级序列对拍 heapq: {'✓ 全一致' if ok else '✗'}（并列元素内部顺序不作约束）")
    # 计时
    t0 = time.perf_counter()
    sch2 = TaskScheduler()
    for name, p in tasks:
        sch2.submit(name, p)
    while len(sch2.h):
        sch2.run_next()
    t_ours = time.perf_counter() - t0
    t0 = time.perf_counter()
    hq = []
    for name, p in tasks:
        heapq.heappush(hq, (-p, name))
    while hq:
        heapq.heappop(hq)
    t_ref = time.perf_counter() - t0
    print(f"  全流程：ch6 MaxHeap {t_ours*1000:8.1f} ms | heapq(C) {t_ref*1000:7.1f} ms → 常数差 {t_ours/t_ref:.0f}×（结构同阶 O(n lg n)）")


# ============================================================
# 3) 堆排序 vs 内置 sorted
# ============================================================
def demo_sort_benchmark():
    print("=" * 60)
    print("应用3：HEAPSORT vs Python sorted（Timsort）")
    for n in (2000, 20_000, 200_000):
        random.seed(n)
        arr = random.sample(range(10 * n), n)
        t0 = time.perf_counter()
        got = MaxHeap(arr).heapsort_inplace()
        t_heap = time.perf_counter() - t0
        t0 = time.perf_counter()
        _ = sorted(arr)
        t_sorted = time.perf_counter() - t0
        ok = got == sorted(arr)
        print(f"  n={n:>7}: heapsort {t_heap*1000:8.1f} ms | sorted(Timsort) {t_sorted*1000:7.1f} ms | 正确 {'✓' if ok else '✗'}")
    print("  → Timsort 系数小 + 对随机数据快 ~lg n/lg n 同阶但实现层完胜；")
    print("    heapsort 的真正底牌是 O(1) 额外空间 + 最坏仍 O(n lg n)，嵌入式/内核场景的菜。")


def main():
    demo_topk()
    demo_scheduler()
    demo_sort_benchmark()


if __name__ == "__main__":
    main()
