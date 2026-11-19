# -*- coding: utf-8 -*-
"""
第13章 应用：红黑树的真实用法
《算法导论（原书第3版）》CLRS ch13

三个实战场景：
  1) 有序集合（std::set / Java TreeMap 语义）：fuzz 对拍 Python set + sorted
  2) 平衡的代价与收益：顺序/随机插入下 BST vs 红黑树 计时
  3) 事件调度器：ceil 查询（找 ≥ t 的最早事件）——日历/定时器内核
"""

import os
import sys
import time
import random
import bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch13_red_black_trees"))
from demo_utils import RedBlackTree


# ============================================================
# 应用 1：有序集合（std::set 语义）
# ============================================================
def demo_sorted_set():
    print("=" * 60)
    print("应用1：有序集合 fuzz 对拍（5000 次随机操作 vs sorted([])）")
    random.seed(42)
    tree = RedBlackTree()
    model = []          # 始终保持有序的参照动态数组
    bad = 0
    for step in range(5000):
        r = random.random()
        k = random.randrange(2000)
        if r < 0.55:
            if tree.search(k) is tree.nil:        # 噢——search 返回 nil 而非 None
                pass
            found = tree.search(k) is not tree.nil
            if not found:
                tree.insert(k)
                bisect.insort(model, k)
        elif r < 0.8:
            found = tree.search(k) is not tree.nil
            if found:
                tree.delete(k)
                idx = bisect.bisect_left(model, k)
                if idx < len(model) and model[idx] == k:
                    model.pop(idx)
        else:
            # in 汤：中序 == model
            got = [kk for kk, _ in tree.inorder()]
            if got != model:
                bad += 1
                if bad == 1:
                    print(f"  ✗ step {step}: 中序与参照不一致")
                    print(f"    got[:5]    = {got[:5]}")
                    print(f"    model[:5]  = {model[:5]}")
                break
    else:
        got = [kk for kk, _ in tree.inorder()]
        if got != model:
            bad += 1
    # 双向校验：树里每个 model 元素都查得到
    ok2 = all(tree.search(k) is not tree.nil for k in model) if bad == 0 else False
    print(f"  fuzz 完成：{5000 if bad else step} 次操作，不一致 {bad} 次",
          "✓" if bad == 0 and ok2 else "✗")
    ok_props, _ = tree.verify()
    print(f"  期末红黑五性质:", "✓" if ok_props else "✗", f"| 元素数 {len(model)}")


# ============================================================
# 应用 2：平衡的代价与收益
# ============================================================
def demo_balance_benchmark():
    print("=" * 60)
    print("应用2：顺序插入 8000 个——朴素 BST vs 红黑树")
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch12_binary_search_trees"))
    from ch12_03_bst_insert_delete import BinarySearchTree

    n = 8000
    keys = list(range(n))
    # 红黑树
    t0 = time.perf_counter()
    rbt = RedBlackTree()
    for k in keys:
        rbt.insert(k)
    t_rbt_ins = time.perf_counter() - t0
    # BST
    import sys as _sys
    _sys.setrecursionlimit(100000)
    t0 = time.perf_counter()
    bst = BinarySearchTree()
    for k in keys:
        bst.insert(k)
    t_bst_ins = time.perf_counter() - t0
    # 搜索基准
    probes = random.sample(range(n * 2), 4000)
    t0 = time.perf_counter()
    h1 = sum(1 for k in probes if rbt.search(k) is not rbt.nil)
    t_rbt_q = time.perf_counter() - t0
    t0 = time.perf_counter()
    h2 = 0
    for k in probes:                    # 迭代搜索，避免递归爆栈
        x = bst.root
        while x is not None and x.key != k:
            x = x.left if k < x.key else x.right
        if x is not None:
            h2 += 1
    t_bst_q = time.perf_counter() - t0
    print(f"  构建耗时: 红黑树 {t_rbt_ins*1000:7.1f} ms | 朴素BST {t_bst_ins*1000:7.1f} ms（朴素 BST 顺序插入每层都要爬整条链 → O(n²)）")
    print(f"  搜索 4000 次: 红黑树 {t_rbt_q*1000:6.1f} ms | 朴素BST {t_bst_q*1000:8.1f} ms（链上逐层爬）")
    print(f"  命中一致: {h1 == h2}（{h1} 个）| 红黑树搜索快 {t_bst_q/max(t_rbt_q,1e-9):.0f} 倍")
    print(f"  树高: RBT {rbt.height()}（≤2·lg(n+1)={2*(n+1).bit_length()}）| BST 退化=链 h={n}")


# ============================================================
# 应用 3：事件调度器（ceil 查询）
# ============================================================
class EventScheduler:
    """定时器内核：红黑树存"时刻"做有序集合。
    schedule(t)    新事件
    next_after(t)  返回 ≥t 的最早事件时刻（ceil 查询）O(lg n)
    pop_next()     弹出最早事件（extract-min 语义）
    """
    def __init__(self):
        self.tree = RedBlackTree()

    def schedule(self, t):
        self.tree.insert(t)

    def next_after(self, t):
        """ceil(T, t)：树中 ≥ t 的最小元素。中序前身：沿树下行收集候选。"""
        best = None
        x = self.tree.root
        while x is not self.tree.nil:
            if x.key >= t:
                best = x.key
                x = x.left               # 找更小的仍 ≥ t 的
            else:
                x = x.right
        return best

    def pop_next(self):
        x = self.tree.root
        if x is self.tree.nil:
            return None
        while x.left is not self.tree.nil:
            x = x.left
        t = x.key
        self.tree.delete(t)
        return t


def demo_scheduler():
    print("=" * 60)
    print("应用3：事件调度器（ceil 查询 / extract-min）")
    random.seed(9)
    sched = EventScheduler()
    times = random.sample(range(1_000_000), 3000)
    for t in times:
        sched.schedule(t)
    # next_after 与 bisect 对拍
    st = sorted(set(times))
    bad = 0
    for t in random.sample(range(1_000_000), 500):
        got = sched.next_after(t)
        i = bisect.bisect_left(st, t)
        expect = st[i] if i < len(st) else None
        if got != expect:
            bad += 1
            print(f"  ✗ next_after({t}) = {got}, 期望 {expect}")
    print(f"  500 次 ceil 查询对拍 bisect：不一致 {bad} 次", "✓" if bad == 0 else "✗")
    # pop_next 应按升序吐出
    first5 = [sched.pop_next() for _ in range(5)]
    first5 = [t for t in first5 if t is not None]
    print(f"  pop_next 前5个: {first5} == sorted 前5: {st[:len(first5)]}:",
          "✓" if first5 == st[:len(first5)] else "✗")


def main():
    demo_sorted_set()
    demo_balance_benchmark()
    demo_scheduler()


if __name__ == "__main__":
    main()
