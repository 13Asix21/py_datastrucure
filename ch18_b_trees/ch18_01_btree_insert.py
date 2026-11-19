# -*- coding: utf-8 -*-
"""
第18章 B树 —— 18.1~18.2 定义与基本操作（插入、分裂）
《算法导论（原书第3版）》CLRS

B树：为磁盘设计的平衡多路搜索树。
  最小度数 t ≥ 2：
  - 每结点至多 2t-1 个 key
  - 除根外每结点至少 t-1 个 key
  - 根至少 1 个 key（除非空树）
  - 内部结点若有 k 个 key 则有 k+1 个孩子
  - 所有叶等深

B-TREE-CREATE / B-TREE-SPLIT-CHILD / B-TREE-INSERT / B-TREE-INSERT-NONFULL
删除（18.3）在 ch18_02。
"""


class BTreeNode:
    __slots__ = ("leaf", "keys", "children", "n")

    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.n = 0

    def _sync(self):
        self.n = len(self.keys)


class BTree:
    def __init__(self, t=2):
        """t = 最小度数。t=2 即 2-3-4 样式的经典教学树。"""
        assert t >= 2
        self.t = t
        self.root = BTreeNode(leaf=True)

    # ---------- 搜索 ----------
    def search(self, k, x=None):
        """B-TREE-SEARCH。O(t·log_t n)"""
        if x is None:
            x = self.root
        i = 0
        while i < x.n and k > x.keys[i]:
            i += 1
        if i < x.n and k == x.keys[i]:
            return (x, i)
        if x.leaf:
            return None
        # 磁盘读(x.children[i])——内存版直接递归
        return self.search(k, x.children[i])

    # ---------- 分裂 ----------
    def split_child(self, x, i):
        """B-TREE-SPLIT-CHILD(x, i)：x 的第 i 个孩子满(2t-1 keys)就劈成两个 t-1。"""
        t = self.t
        z = BTreeNode()
        y = x.children[i]
        z.leaf = y.leaf
        # y 的后半部分搬给 z
        z.keys = y.keys[t:]              # 右半 t-1 个
        median = y.keys[t - 1]           # 中间 key 上提
        y.keys = y.keys[:t - 1]          # y 留左半 t-1 个
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        x.keys.insert(i, median)
        x.children.insert(i + 1, z)
        y._sync(); z._sync(); x._sync()

    # ---------- 插入 ----------
    def insert(self, k):
        """B-TREE-INSERT：根满先整棵长高再插。"""
        r = self.root
        if r.n == 2 * self.t - 1:
            s = BTreeNode(leaf=False)
            s.children = [r]
            self.root = s
            self.split_child(s, 0)
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def _insert_nonfull(self, x, k):
        """B-TREE-INSERT-NONFULL。"""
        if x.leaf:
            # 插入位
            i = x.n - 1
            x.keys.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
            x._sync()
        else:
            i = x.n - 1
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if x.children[i].n == 2 * self.t - 1:
                self.split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.children[i], k)

    # ---------- 校验与展示 ----------
    def verify(self):
        errs = []
        t = self.t

        def chk(x, depth, is_root):
            if x.n != len(x.keys):
                errs.append(f"n 不同步 @ {x.keys}")
            if not x.leaf and len(x.children) != x.n + 1:
                errs.append(f"孩子数错 @ keys={x.keys}: {len(x.children)} != {x.n+1}")
            if is_root:
                if not x.leaf and x.n < 1:
                    errs.append("根内部结点 key 数 < 1")
            else:
                if x.n < t - 1 or x.n > 2 * t - 1:
                    errs.append(f"key 数越界 @ {x.keys}: {x.n}")
            if x.leaf and depth is not None:
                leaf_depths.append(depth)
            for c in x.children:
                chk(c, depth + 1 if depth is not None else None, False)
            # 升序
            if x.keys != sorted(x.keys):
                errs.append(f"key 不升序 @ {x.keys}")

        leaf_depths = []
        chk(self.root, 0, True)
        if leaf_depths and len(set(leaf_depths)) != 1:
            errs.append(f"叶不等深: {sorted(set(leaf_depths))}")
        return len(errs) == 0, errs

    def height(self):
        h, x = 0, self.root
        while not x.leaf:
            h += 1
            x = x.children[0]
        return h

    def inorder(self):
        out = []
        def walk(x):
            if x.leaf:
                out.extend(x.keys)
            else:
                for i in range(x.n):
                    walk(x.children[i])
                    out.append(x.keys[i])
                walk(x.children[x.n])
        walk(self.root)
        return out

    def print_tree(self):
        def dump(x, depth=0):
            print("  " * depth + f"[{' '.join(map(str, x.keys))}]")
            for c in x.children:
                dump(c, depth + 1)
        dump(self.root)


def demo():
    print("=" * 60)
    print("18.1/18.2 B树（t=3）插入与分裂")
    t = BTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 22, 40, 50, 60, 70, 80, 90, 100, 55, 65, 35, 45]
    for k in keys:
        t.insert(k)
        ok, errs = t.verify()
        if not ok:
            print(f"  ✗ 插入 {k} 后 B树性质破坏: {errs[:2]}")
            break
    ok, _ = t.verify()
    print(f"插入 {len(keys)} 个 key；结构校验 {'✓' if ok else '✗'}")
    print("树形:")
    t.print_tree()
    print("中序(升序):", t.inorder() == sorted(keys), "(与 sorted 对比)")
    print("树高:", t.height())
    for k in (6, 65, 100, 99):
        print(f"search({k}):", "命中" if t.search(k) else "未命中")


if __name__ == "__main__":
    demo()
