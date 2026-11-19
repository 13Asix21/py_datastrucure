# -*- coding: utf-8 -*-
"""
第12章 应用：二叉搜索树的真实用法
《算法导论（原书第3版）》CLRS ch12

三个实战场景：
  1) 动态电话簿：insert/delete/search 混合操作 vs 排序数组二分 vs 线性表
  2) 范围查询：BST 剪枝枚举 vs 全表线性过滤（数据库索引的本质）
  3) 有序插入退化实验：BST 为什么会变链表（引出 ch13 红黑树的需求）
"""

import os
import sys
import time
import random
import bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch12_03_bst_insert_delete import BinarySearchTree


# ============================================================
# 应用 1：动态电话簿
# ============================================================
def demo_phonebook():
    print("=" * 60)
    print("应用1：动态电话簿（10 万次 查/插/删 混合）")
    random.seed(7)
    n = 100_000
    keys = random.sample(range(1_000_000), n)

    bst = BinarySearchTree()
    sorted_arr = sorted(random.sample(range(1_000_000), 2000))  # 排序数组参照
    for k in sorted_arr:
        bst.insert(k)

    # --- BST 查询 ---
    probes = random.sample(keys, 2000)
    t0 = time.perf_counter()
    hits = sum(1 for k in probes if bst.search(k) is not None)
    t_bst = time.perf_counter() - t0

    # --- 排序数组二分（静态参照）---
    t0 = time.perf_counter()
    hits2 = sum(1 for k in probes if bisect.bisect_left(sorted_arr, k) < len(sorted_arr)
                and sorted_arr[bisect.bisect_left(sorted_arr, k)] == k)
    t_bi = time.perf_counter() - t0

    print(f"  命中数一致: {hits == hits2} ({hits})")
    print(f"  BST 搜索 2000 次: {t_bst*1000:8.2f} ms | 排序数组二分(需先全排序): {t_bi*1000:6.3f} ms")
    print("  → 二分查找快（C 实现常数小），但它不支持 O(h) 动态插入——每次插入 O(n) 搬移；")
    print("    BST 的价值 = 查找 O(h) 且插删也 O(h)。静态数据用数组，动态数据用树。")

    # --- 动态混合操作：BST vs list 的成员维护 ---
    live_bst = BinarySearchTree()
    live_list = []
    ops_keys = random.sample(range(1_000_000), 2000)
    t0 = time.perf_counter()
    for k in ops_keys:
        live_bst.insert(k)
    t_bst_ins = time.perf_counter() - t0
    t0 = time.perf_counter()
    for k in ops_keys:
        live_list.append(k)
    t_list_ins = time.perf_counter() - t0
    print(f"  动态插入 2000 个：BST {t_bst_ins*1000:7.2f} ms | list append {t_list_ins*1000:6.3f} ms（append 当然快）")
    probes = random.sample(ops_keys, 500) + random.sample(range(1_000_000), 500)
    t0 = time.perf_counter()
    h1 = sum(1 for k in probes if live_bst.search(k) is not None)
    t_bst_q = time.perf_counter() - t0
    st = set(live_list)
    t0 = time.perf_counter()
    h2 = sum(1 for k in probes if k in st)
    t_set_q = time.perf_counter() - t0
    t0 = time.perf_counter()
    h3 = sum(1 for k in probes[:100] if any(x == k for x in live_list))
    t_lin_q = (time.perf_counter() - t0) * len(probes) / 100
    print(f"  查 1000 次：BST {t_bst_q*1000:7.2f} ms | set {t_set_q*1000:6.3f} ms | 线性扫(折算) {t_lin_q*1000:9.2f} ms")
    print(f"  命中一致: {h1 == h2}，BST 比线性扫快 {t_lin_q/t_bst_q:.0f} 倍")


# ============================================================
# 应用 2：范围查询（数据库索引本质）
# ============================================================
def bst_range(bst, lo, hi, node=None, out=None):
    """BST 范围枚举：剪枝——左子树只有 >lo 才进，右子树只有 <hi 才进。"""
    if out is None:
        out, node = [], bst.root
    if node is None:
        return out
    if node.key > lo:                       # 左子树可能藏有 [lo,hi]
        bst_range(bst, lo, hi, node.left, out)
    if lo <= node.key <= hi:
        out.append(node.key)
    if node.key < hi:                       # 右子树同理
        bst_range(bst, lo, hi, node.right, out)
    return out


def demo_range_query():
    print("=" * 60)
    print("应用2：范围查询 [70000, 70500)（SQL: WHERE id BETWEEN）")
    random.seed(11)
    keys = random.sample(range(100_000), 20_000)
    bst = BinarySearchTree()
    for k in keys:
        bst.insert(k)
    lo, hi = 70_000, 70_500
    t0 = time.perf_counter()
    got = bst_range(bst, lo, hi - 1)
    t_bst = time.perf_counter() - t0
    t0 = time.perf_counter()
    expect = sorted(k for k in keys if lo <= k < hi)
    t_lin = time.perf_counter() - t0
    ok = got == expect
    print(f"  命中 {len(got)} 个键，与全表过滤对拍: {'✓' if ok else '✗'}")
    print(f"  BST 剪枝枚举: {t_bst*1000:.3f} ms | 线性全表过滤: {t_lin*1000:.3f} ms → 快 {t_lin/t_bst:.1f} 倍")
    print("  → 数据量越大差距越大：全表 O(n) vs 剪枝 O(h+k)，k=命中数")


# ============================================================
# 应用 3：有序插入退化实验（引出红黑树）
# ============================================================
def demo_degeneration():
    print("=" * 60)
    print("应用3：顺序插入退化实验——BST 的阿喀琉斯之踵")

    def height(root):
        """迭代求高（顺序插入的树深 4000+，递归会爆栈）。"""
        h = 0
        x = root
        while x is not None:                # 退化链：一路向右就是全部深度
            h += 1
            x = x.right
        # 通用树需 BFS；本题树是链，右链即最深路径。为稳妥仍做完整 BFS：
        h = 0
        level = [root] if root else []
        while level:
            h += 1
            nxt = []
            for node in level:
                for c in (node.left, node.right):
                    if c is not None:
                        nxt.append(c)
            level = nxt
        return h

    for n in (1000, 2000, 4000):
        bst = BinarySearchTree()
        for k in range(n):                  # 顺序插入 → 完美链
            bst.insert(k)
        h = height(bst.root)
        print(f"  顺序插 {n:5d} 个 → 树高 {h:5d}（随机插入期望仅 ≈ 2·lg n = {2*(n.bit_length()-1):2d}）")
    print("  随机插入时树高 ≈ 2·lg n（期望平衡），但排序数据让 BST 查找跌回 O(n)。")
    print("  → 这正是 ch13 红黑树存在的意义：旋转强制 h ≤ 2·lg(n+1)，任何插入序都不怕。")


def main():
    demo_phonebook()
    demo_range_query()
    demo_degeneration()


if __name__ == "__main__":
    main()
