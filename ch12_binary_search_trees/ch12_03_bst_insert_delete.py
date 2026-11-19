# -*- coding: utf-8 -*-
"""
第12章 二叉搜索树 —— 12.3 插入和删除
《算法导论（原书第3版）》CLRS

TREE-INSERT：O(h)，总挂在叶子上。
TREE-DELETE 三种情形：
  z 无孩子      → 直接摘掉
  z 有一个孩子  → 孩子顶替
  z 有两个孩子  → 用后继 y（z 右子树最小）顶替 z 的 key，
                  再把 y 的右孩子接到 y 的父上（y 必无左孩子）
"""


class Node:
    __slots__ = ("key", "p", "left", "right")

    def __init__(self, key):
        self.key = key
        self.p = None
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    # ---------- 基础 ----------
    def insert(self, k):
        """TREE-INSERT。O(h)"""
        z = Node(k)
        y, x = None, self.root
        while x is not None:
            y = x
            x = x.left if z.key < x.key else x.right
        z.p = y
        if y is None:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        return z

    def transplant(self, u, v):
        """TRANSPLANT：用子树 v 替换子树 u（只动父指针，不管 v 内部）。"""
        if u.p is None:
            self.root = v
        elif u is u.p.left:
            u.p.left = v
        else:
            u.p.right = v
        if v is not None:
            v.p = u.p

    def delete(self, z):
        """TREE-DELETE 三情形（正式版，删除结点 z 本身）。O(h)"""
        if z.left is None:                    # 情形 1/2：无左孩子
            self.transplant(z, z.right)
        elif z.right is None:                 # 情形 2：无右孩子
            self.transplant(z, z.left)
        else:                                  # 情形 3：双子在
            y = self.minimum(z.right)          # 后继
            if y.p is not z:                   # y 不紧贴 z → 先把 y 的右子提上来
                self.transplant(y, y.right)
                y.right = z.right
                y.right.p = y
            self.transplant(z, y)
            y.left = z.left
            y.left.p = y
        return z.key

    def minimum(self, x):
        while x.left is not None:
            x = x.left
        return x

    def search(self, k):
        x = self.root
        while x is not None and x.key != k:
            x = x.left if k < x.key else x.right
        return x

    def inorder(self):
        acc = []
        def walk(n):
            if n:
                walk(n.left); acc.append(n.key); walk(n.right)
        walk(self.root)
        return acc


def demo():
    print("=" * 60)
    print("12.3 TREE-INSERT / TREE-DELETE")
    bst = BinarySearchTree()
    keys = (15, 6, 3, 2, 4, 7, 13, 9, 18, 17, 20)
    for k in keys:
        bst.insert(k)
    print("初始中序:", bst.inorder())

    print()
    print("情形1：删除叶子结点 4")
    bst.delete(bst.search(4))
    print("  中序:", bst.inorder())

    print("情形2：删除只有一个孩子的 3（孩子 2 顶上）")
    bst.delete(bst.search(3))
    print("  中序:", bst.inorder())

    print("情形3：删除有两个孩子的 15（后继 17 顶替）")
    bst.delete(bst.search(15))
    print("  中序:", bst.inorder())

    print()
    print("重建后全量删光（随机顺序）：")
    import random
    bst = BinarySearchTree()
    for k in keys:
        bst.insert(k)
    order = list(keys)
    random.shuffle(order)
    for k in order:
        node = bst.search(k)
        assert node is not None, f"找不到 {k}"
        bst.delete(node)
        remain = bst.inorder()
        assert all(x != k for x in remain), f"{k} 没删干净"
    print("  全部删除后中序:", bst.inorder(), "| root =", bst.root, "→ 结构完好 ✓")


if __name__ == "__main__":
    demo()
