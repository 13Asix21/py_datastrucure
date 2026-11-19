# -*- coding: utf-8 -*-
"""
第14章 数据结构的扩张 —— 14.1~14.2 动态顺序统计（OS 树）
《算法导论（原书第3版）》CLRS

红黑树 + size 字段：每个结点存 x.size = x 为根子树的结点数。
支持：
  OS-SELECT(x, i)   —— 子树中第 i 小的 key     O(lg n)
  OS-RANK(T, x)     —— key 在全集中的排名      O(lg n)
插入/删除 时维护 size（增量 O(lg n)）。
"""


class OSNode:
    __slots__ = ("key", "color", "size", "p", "left", "right")

    def __init__(self, key, color="R"):
        self.key = key
        self.color = color
        self.size = 1
        self.p = None
        self.left = None
        self.right = None


RED, BLACK = "R", "B"


class OSTree:
    """顺序统计树（红黑树底座 + size 扩张）。NIL 用哨兵处理。"""

    def __init__(self):
        self.nil = OSNode(None, BLACK)
        self.nil.size = 0
        self.nil.left = self.nil.right = self.nil.p = self.nil
        self.root = self.nil

    # ---------- 基础红黑操作（带 size 维护）----------
    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.nil:
            y.left.p = x
        y.p = x.p
        if x.p is self.nil:
            self.root = y
        elif x is x.p.left:
            x.p.left = y
        else:
            x.p.right = y
        y.left = x
        x.p = y
        y.size = x.size                      # ← 14.1 扩张：size 跟着旋转走
        x.size = x.left.size + x.right.size + 1

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right is not self.nil:
            x.right.p = y
        x.p = y.p
        if y.p is self.nil:
            self.root = x
        elif y is y.p.left:
            y.p.left = x
        else:
            y.p.right = x
        x.right = y
        y.p = x
        x.size = y.size
        y.size = y.left.size + y.right.size + 1

    def insert(self, k):
        """RB-INSERT + size 维护。O(lg n)"""
        z = OSNode(k, RED)
        z.left = z.right = self.nil
        y, x = self.nil, self.root
        while x is not self.nil:
            y = x
            x.size += 1                       # ← 沿路径所有祖先 size+1
            x = x.left if z.key < x.key else x.right
        z.p = y
        if y is self.nil:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        self._insert_fixup(z)
        return z

    def _insert_fixup(self, z):
        while z.p.color == RED:
            if z.p is z.p.p.left:
                y = z.p.p.right
                if y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z is z.p.right:
                        z = z.p
                        self.left_rotate(z)
                    z.p.color = BLACK
                    z.p.p.color = RED
                    self.right_rotate(z.p.p)
            else:
                y = z.p.p.left
                if y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z is z.p.left:
                        z = z.p
                        self.right_rotate(z)
                    z.p.color = BLACK
                    z.p.p.color = RED
                    self.left_rotate(z.p.p)
        self.root.color = BLACK

    # ---------- 14.1 顺序统计操作 ----------
    def os_select(self, x, i):
        """OS-SELECT(x, i)：x 子树中第 i 小。O(lg n)"""
        r = x.left.size + 1                  # x 在其子树中的排名
        if i == r:
            return x
        elif i < r:
            return self.os_select(x.left, i)
        return self.os_select(x.right, i - r)

    def os_rank(self, k):
        """OS-RANK(T, x)：key=k 的排名。O(lg n)"""
        x = self._search(k)
        if x is self.nil:
            return None
        r = x.left.size + 1
        y = x
        while y is not self.root:
            if y is y.p.right:
                r += y.p.left.size + 1
            y = y.p
        return r

    def _search(self, k):
        x = self.root
        while x is not self.nil and x.key != k:
            x = x.left if k < x.key else x.right
        return x

    # ---------- 校验 ----------
    def verify_sizes(self):
        errs = []
        def chk(x):
            if x is self.nil:
                return 0
            if x.size != x.left.size + x.right.size + 1:
                errs.append(f"size 错误 @key={x.key}: 存 {x.size}, 应为 {x.left.size + x.right.size + 1}")
            chk(x.left); chk(x.right)
            return x.size
        chk(self.root)
        return len(errs) == 0, errs

    def inorder(self, x=None, acc=None):
        if acc is None:
            acc, x = [], self.root
        if x is not self.nil:
            self.inorder(x.left, acc)
            acc.append((x.key, x.size))
            self.inorder(x.right, acc)
        return acc


def demo():
    print("=" * 60)
    print("14.1 顺序统计树 OS-SELECT / OS-RANK")
    import random
    random.seed(3)
    keys = random.sample(range(100), 40)
    t = OSTree()
    for k in keys:
        t.insert(k)
    ok, errs = t.verify_sizes()
    print(f"插入 40 个 key，size 全程维护 {'✓' if ok else '✗ {errs[:2]}'}")
    sorted_keys = sorted(keys)
    print("中序(升序) 前 10:", [k for k, _ in t.inorder()][:10])
    # OS-SELECT 校验：第 i 小应等于 sorted[i-1]
    all_ok = True
    for i in range(1, len(sorted_keys) + 1, 7):
        node = t.os_select(t.root, i)
        expect = sorted_keys[i - 1]
        match = node.key == expect
        all_ok &= match
        print(f"  OS-SELECT({i:2d}) = {node.key:3d}  应为 {expect:3d}  {'✓' if match else '✗'}")
    # OS-RANK 校验
    for k in (sorted_keys[4], sorted_keys[17], sorted_keys[33]):
        r = t.os_rank(k)
        expect = sorted_keys.index(k) + 1
        print(f"  OS-RANK({k:3d}) = {r:2d}  应为 {expect:2d}  {'✓' if r == expect else '✗'}")
        all_ok &= (r == expect)
    print("整体校验:", "✓" if all_ok else "✗")


if __name__ == "__main__":
    demo()
