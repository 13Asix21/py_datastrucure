# -*- coding: utf-8 -*-
"""
B+ 树 —— CLRS ch18 引申 + 系统架构师考点
软考原话："B 树、B+ 树的基本概念（结合数据库索引考查）"

B+ 树 vs B 树（CLRS 18 章）的三个工程差异：
  1. 内部结点只存路由键：数据 records 全在叶子（MySQL InnoDB 主键索引）
  2. 分裂时键被"复制"上提（B 树是"移动"）
  3. 叶结点串成双向链表：范围扫描 = 定位 + 顺链读（数据库 range scan 的 O(k) 骨架）

对拍：单点查询 vs bisect；范围扫描 vs B 树递归剪枝（ch18_app 的 btree_range_scan）；
     全删后结构校验。
"""

import random


class BPTNode:
    __slots__ = ("leaf", "keys", "children", "next", "prev", "parent")

    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []      # 内部结点用；叶子存记录指针（演示中即 key 本体）
        self.next = None        # 叶链（右向）
        self.prev = None
        self.parent = None


class BPlusTree:
    """B+ 树（最小度数 t：结点 [t-1, 2t-1] 键，分裂于 2t-1）。"""

    def __init__(self, t=3):
        assert t >= 2
        self.t = t
        self.root = BPTNode(leaf=True)
        self._len = 0

    # ---------------- 查询 ----------------
    def search(self, k):
        """单点查询：走到叶，二分找。O(lg n)
        B+ 路由约定（与 insert 一致）：孩子 i 的键域 [keys[i-1], keys[i]) 左闭右开，
        即路由键 k == keys[i] 时应进右孩子 i+1 —— bisect_right 语义。"""
        x = self.root
        while not x.leaf:
            i = self._upper_bound(x.keys, k)
            x = x.children[i]
        i = self._lower_bound(x.keys, k)
        if i < len(x.keys) and x.keys[i] == k:
            return True
        return False

    def _upper_bound(self, keys, k):
        lo, hi = 0, len(keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if keys[mid] <= k:
                lo = mid + 1
            else:
                hi = mid
        return lo

    @staticmethod
    def _lower_bound(keys, k):
        """首个 >= k 的位置（bisect_left 语义，手写避免依赖）。"""
        lo, hi = 0, len(keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if keys[mid] < k:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def range_scan(self, lo, hi):
        """范围扫描 [lo, hi]：定位 lo 所在叶 → 顺叶链读到超界为止。
        O(lg n + k) —— 数据库 range scan 的骨架。"""
        x = self.root
        while not x.leaf:
            x = x.children[self._upper_bound(x.keys, lo)]
        out = []
        while x is not None:
            for k in x.keys:
                if k > hi:
                    return out
                if k >= lo:
                    out.append(k)
            x = x.next
        return out

    # ---------------- 插入（预分裂一路下行）----------------
    def insert(self, k):
        """满根先长高；每个下行结点满则先分裂（预分裂，等价 18 章手法）。O(lg n)"""
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BPTNode(leaf=False)
            root.parent = s
            s.children.append(root)
            self._split_child(s, 0)
            self.root = s
        self._insert_nonfull(self.root, k)
        self._len += 1

    def _split_child(self, parent, i):
        """分裂 parent 第 i 个孩子。叶子分裂：中键复制上提 + 建叶链。"""
        t = self.t
        y = parent.children[i]
        z = BPTNode(leaf=y.leaf)
        z.parent = parent
        if y.leaf:
            # 叶子：中键复制上提（路由），且必须保留在右叶 z 的队首（B+ 数据全在叶）
            up = y.keys[t - 1]
            z.keys = y.keys[t - 1:]               # 右叶含中键副本
            y.keys = y.keys[:t - 1]
            # 叶链缝合
            z.next = y.next
            if z.next:
                z.next.prev = z
            y.next = z
            z.prev = y
        else:
            # 内部：中键移动上提
            up = y.keys[t - 1]
            z.keys = y.keys[t:]
            y.keys = y.keys[:t - 1]
            z.children = y.children[t:]
            y.children = y.children[:t]
            for c in z.children:
                c.parent = z
        parent.keys.insert(i, up)
        parent.children.insert(i + 1, z)

    def _insert_nonfull(self, x, k):
        while not x.leaf:
            i = self._upper_bound(x.keys, k)      # 与 search 同约定：k==keys[i] 走右
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                i = self._upper_bound(x.keys, k)  # 分裂后重算路由
            x = x.children[i]
        i = self._lower_bound(x.keys, k)
        x.keys.insert(i, k)

    # ---------------- 校验 ----------------
    def verify(self):
        """B+ 树结构不变量：键界、叶等深、叶链完整、内部无数据。"""
        errs = []
        t = self.t
        depths = []

        def chk(x, d, lo, hi):
            if not x.leaf and (len(x.keys) < 1 and x is not self.root):
                errs.append("内部结点空键")
            if x is not self.root and not (t - 1 <= len(x.keys) <= 2 * t - 1):
                errs.append(f"键数越界 @ {x.keys[:3]}: {len(x.keys)}")
            for idx, key in enumerate(x.keys):
                if key < lo or key >= hi:
                    errs.append(f"键越界 {key} ∉ [{lo},{hi})")
            if x.leaf:
                depths.append(d)
                if x.keys != sorted(x.keys):
                    errs.append("叶键不升序")
            else:
                if len(x.children) != len(x.keys) + 1:
                    errs.append("孩子数 != 键数+1")
                for ci, c in enumerate(x.children):
                    if c.parent is not x:
                        errs.append("父指针断裂")
                    clo = x.keys[ci - 1] if ci > 0 else lo
                    chi = x.keys[ci] if ci < len(x.keys) else hi
                    chk(c, d + 1, clo, chi)

        chk(self.root, 0, float("-inf"), float("inf"))
        if len(set(depths)) > 1:
            errs.append(f"叶不等深 {sorted(set(depths))}")
        # 叶链 vs 中序
        leaves = []
        x = self.root
        while not x.leaf:
            x = x.children[0]
        while x:
            leaves.extend(x.keys)
            x = x.next
        # 全树键数一致性：中序收集
        allkeys = []
        def walk(x):
            if x.leaf:
                allkeys.extend(x.keys)
            else:
                for c in x.children:
                    walk(c)
        walk(self.root)
        if leaves != allkeys or leaves != sorted(allkeys):
            errs.append("叶链与全树键不一致（叶链应=全部键升序）")
        if len(allkeys) != self._len:
            errs.append(f"计数 {len(allkeys)} != {self._len}")
        return len(errs) == 0, errs

    def height(self):
        h, x = 0, self.root
        while not x.leaf:
            h += 1
            x = x.children[0]
        return h


def demo_baseline():
    print("=" * 60)
    print("B+ 树基础（t=3）：插入 500 随机键 + 结构校验")
    random.seed(5)
    keys = random.sample(range(10_000), 500)
    t = BPlusTree(t=3)
    for k in keys:
        t.insert(k)
        ok, errs = t.verify()
        if not ok:
            print(f"  ✗ 插 {k} 后: {errs[:2]}")
            return
    ok, errs = t.verify()
    print(f"  500 键结构校验（键界/叶等深/叶链/计数）:", "✓" if ok else f"✗ {errs[:2]}")
    print(f"  树高 {t.height()}（500 键、t=3：3 层即可肌肉记忆——数据库页 16KB 能塞几百键，7 亿行也只 3 层）")


def demo_vs_btree():
    print("=" * 60)
    print("范围扫描对比：B+ 叶链顺读 vs B 树递归剪枝（ch18_app 同场景）")
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from ch18_b_trees.ch18_app_btree_app import btree_range_scan
    from ch18_b_trees.ch18_02_btree_delete import BTree
    import time

    random.seed(5)
    keys = random.sample(range(1_000_000), 20_000)
    bp = BPlusTree(t=64)
    bt = BTree(t=64)
    for k in keys:
        bp.insert(k)
        bt.insert(k)
    lo, hi = 500_000, 501_000
    # 正确性对拍
    got_bp = bp.range_scan(lo, hi)
    got_bt = btree_range_scan(bt, lo, hi)
    expect = sorted(k for k in keys if lo <= k <= hi)
    print(f"  [500000,501000] B+叶链命中 {len(got_bp)} | B树剪枝 {len(got_bt)} | 全表参照 {len(expect)}:",
          "✓ 三方一致" if got_bp == got_bt == expect else "✗")
    # 效率
    probes = 200
    t0 = time.perf_counter()
    for _ in range(probes):
        bp.range_scan(lo, hi)
    t_bp = (time.perf_counter() - t0) / probes
    t0 = time.perf_counter()
    for _ in range(probes):
        btree_range_scan(bt, lo, hi)
    t_bt = (time.perf_counter() - t0) / probes
    print(f"  单次范围扫描：B+叶链 {t_bp*1000:.3f} ms | B树递归剪枝 {t_bt*1000:.3f} ms → B+ 快 {t_bt/t_bp:.1f}×")
    print("  读数：叶链是纯顺序读（模拟磁盘:命中 k 页连续读）；B 树范围要反复升降树。")
    print("        加上『内部结点不含 data → 同页塞更多键 → 树更矮』——这就是 InnoDB 选 B+ 的两个理由。")


def demo_point_query():
    print("=" * 60)
    print("单点查询对拍 bisect（5000 键，2000 查询）")
    import bisect
    random.seed(11)
    keys = random.sample(range(100_000), 5000)
    t = BPlusTree(t=32)
    for k in keys:
        t.insert(k)
    sk = sorted(keys)
    bad = 0
    probes = [random.randrange(100_000) for _ in range(2000)]
    for q in probes:
        got = t.search(q)
        i = bisect.bisect_left(sk, q)
        want = i < len(sk) and sk[i] == q
        if got != want:
            bad += 1
    print(f"  2000 点查 vs bisect:", "✓ 全一致" if bad == 0 else f"✗ {bad}")


def main():
    demo_baseline()
    demo_point_query()
    demo_vs_btree()


if __name__ == "__main__":
    main()
