# -*- coding: utf-8 -*-
"""
第18章 应用：B树 —— 磁盘索引的真实用法
《算法导论（原书第3版）》CLRS ch18

B树为磁盘而生：一次"结点访问"= 一次磁盘页 I/O。
对于 7 亿条记录（MySQL InnoDB 主键索引的真实量级）：
  - 二叉树高 lg(7e8) ≈ 30 → 30 次页读
  - B树(t=256)高 log_t(n) ≈ 3~4 → 3~4 次页读

本 demo：
  1) 模拟磁盘：给 B树 与 BST 装"页读取计数器"，对比同一批查询的 I/O 次数
  2) 范围扫描：B树的叶序列扫描 vs 全表线性扫（数据库 range scan 的本质）
  3) 不同 t（阶）下的树高对比 —— 为什么数据库选 t≈几百
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch18_02_btree_delete import BTree
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ch12_binary_search_trees"))
from ch12_03_bst_insert_delete import BinarySearchTree


# ============================================================
# 1) 磁盘 I/O 模拟：给两种树装"访问探针"
# ============================================================
class IOCountingBTree(BTree):
    page_reads = 0
    def search(self, k, x=None):
        if x is None:
            x = self.root
        IOCountingBTree.page_reads += 1          # 每访问一个结点 = 1 次页读
        i = 0
        while i < x.n and k > x.keys[i]:
            i += 1
        if i < x.n and k == x.keys[i]:
            return (x, i)
        if x.leaf:
            return None
        return self.search(k, x.children[i])


class IOCountingBST(BinarySearchTree):
    node_visits = 0
    def search(self, k):
        IOCountingBST.node_visits += 1
        x = self.root
        while x is not None and x.key != k:
            IOCountingBST.node_visits += 1
            x = x.left if k < x.key else x.right
        return x


def demo_disk_io():
    print("=" * 60)
    print("应用1：磁盘页 I/O 对比（2 万条记录的索引）")
    random.seed(5)
    n = 20_000
    keys = random.sample(range(1_000_000), n)

    bt = IOCountingBTree(t=64)
    for k in keys:
        bt.insert(k)
    bst = IOCountingBST()
    for k in keys:
        bst.insert(k)

    probes = [random.choice(keys) for _ in range(2000)]
    IOCountingBTree.page_reads = 0
    IOCountingBST.node_visits = 0
    for k in probes:
        assert bt.search(k) is not None
        assert bst.search(k) is not None
    io_bt = IOCountingBTree.page_reads / len(probes)
    io_bst = IOCountingBST.node_visits / len(probes)
    print(f"  每次查询平均页读：B树(t=64) {io_bt:5.2f} 页 | 二叉BST {io_bst:7.2f} 页")
    print(f"  → 访问次数比 {io_bst/io_bt:.1f} 倍。磁盘 1 页 ~10ms：一次查询 B树 ≈ {io_bt*10:.0f}ms，BST ≈ {io_bst*10:.0f}ms")
    print(f"  B树高 {bt.height()+1} 层 vs BST 树高 ~{io_bst:.0f}（随机插入期望 ≈ 1.39·lg n ≈ 20）")
    print("  真实 DB 场景（n=7e8，t=512，页 16KB）：B树高仅 3，全表扫描才是灾难，逐点查询 3 页命中。")


# ============================================================
# 2) 范围扫描（range scan）
# ============================================================
def btree_range_scan(bt, lo, hi):
    """B树范围扫描：递归下行 + 子树剪枝（教科书 18.1(b) 性质的直接应用）。
    内部结点 x 的孩子 i 覆盖 key 区间 (keys[i-1], keys[i])（端点用 ±inf 补齐），
    只递归与 [lo,hi] 相交的孩子。"""
    out = []

    def walk(x):
        for i in range(x.n):
            left_bound = x.keys[i - 1] if i > 0 else float("-inf")
            right_bound = x.keys[i]
            if not x.leaf and left_bound < hi and right_bound > lo:
                walk(x.children[i])               # 左孩子与区间相交
            if lo <= right_bound <= hi:
                out.append(right_bound)            # 该 key 本身落界内
        if not x.leaf:
            last = x.keys[-1]
            if last < hi:                          # 最右孩子覆盖 (last, +inf)
                walk(x.children[x.n])

    walk(bt.root)
    return out


def demo_range_scan():
    print("=" * 60)
    print("应用2：范围扫描 [50000, 51000]（2 万条中）")
    random.seed(5)
    keys = random.sample(range(1_000_000), 20_000)
    bt = BTree(t=64)
    for k in keys:
        bt.insert(k)
    lo, hi = 500_000, 501_000
    t0 = time.perf_counter()
    got = btree_range_scan(bt, lo, hi)
    t_bt = time.perf_counter() - t0
    t0 = time.perf_counter()
    expect = sorted(k for k in keys if lo <= k <= hi)
    t_lin = time.perf_counter() - t0
    ok = sorted(got) == expect
    print(f"  命中 {len(expect)} 条，结果对拍: {'✓' if ok else '✗'}")
    print(f"  B树有序扫描 {t_bt*1000:7.3f} ms | 全表线性扫描 {t_lin*1000:7.3f} ms")
    print("  → 大数据上全表扫输出代价 O(n I/O)；B树只读命中路径 O(h + k) 页。")


# ============================================================
# 3) 阶数 t 的影响：树高 = I/O 乘数
# ============================================================
def demo_tuning_t():
    print("=" * 60)
    print("应用3：阶数 t 对树高的影响（n=100000）")
    from math import log2, ceil
    for t in (2, 16, 64, 256, 1024):
        bt = IOCountingBTree(t=t)
        sample = random.sample(range(1_000_000), 20_000)
        for k in sample:
            bt.insert(k)
        # 理论高：≤ log_t((n+1)/2)
        n = len(bt.inorder())
        h_theory = ceil(log2(n + 1) / log2(t))
        print(f"  t={t:5d} → 实际高 {bt.height()+1} 层 | 理论上界 ~{h_theory} | 适合的磁盘页大小 ≈ {(2*t-1)*(8 if t<200 else 42)}B+")
    print("  → 磁盘页 4KB~16KB 能塞几百个 key，所以数据库索引用大 t 的 B+树，树高仅 3~4 层。")


def main():
    demo_disk_io()
    demo_range_scan()
    demo_tuning_t()


if __name__ == "__main__":
    main()
