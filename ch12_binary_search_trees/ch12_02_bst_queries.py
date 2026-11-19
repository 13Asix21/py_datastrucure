# -*- coding: utf-8 -*-
"""
第12章 二叉搜索树 —— 12.2 查询二叉搜索树
《算法导论（原书第3版）》CLRS

SEARCH / MINIMUM / MAXIMUM / SUCCESSOR / PREDECESSOR
全部 O(h)，h 为树高（平衡时 h=O(lg n)，最坏退化成链 h=n）。
此处保持 12.1 的 Node/insert 复用。
"""


class Node:
    __slots__ = ("key", "p", "left", "right")

    def __init__(self, key):
        self.key = key
        self.p = None
        self.left = None
        self.right = None


def tree_insert(bst, z):
    y, x = None, bst.root
    while x is not None:
        y = x
        x = x.left if z.key < x.key else x.right
    z.p = y
    if y is None:
        bst.root = z
    elif z.key < y.key:
        y.left = z
    else:
        y.right = z
    return z


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, k):
        return tree_insert(self, Node(k))

    # ---------- 12.2 查询 ----------
    def tree_search(self, k, x=None):
        """TREE-SEARCH：递归版。O(h)"""
        if x is None:
            x = self.root
            if x is None:
                return None
        if k == x.key:
            return x
        if k < x.key:
            return self.tree_search(k, x.left) if x.left else None
        return self.tree_search(k, x.right) if x.right else None

    def iterative_tree_search(self, k):
        """ITERATIVE-TREE-SEARCH：循环版（更实用，省栈）。O(h)"""
        x = self.root
        while x is not None and k != x.key:
            x = x.left if k < x.key else x.right
        return x

    def tree_minimum(self, x=None):
        """TREE-MINIMUM：一路向左。O(h)"""
        if x is None:
            x = self.root
        while x is not None and x.left is not None:
            x = x.left
        return x

    def tree_maximum(self, x=None):
        """TREE-MAXIMUM：一路向右。O(h)"""
        if x is None:
            x = self.root
        while x is not None and x.right is not None:
            x = x.right
        return x

    def tree_successor(self, x):
        """TREE-SUCCESSOR：中序后继。
        case 1: 有右子树 → 右子树最小值
        case 2: 无右子树 → 沿父链上溯，找到第一个"左拐上去"的祖先
        """
        if x.right is not None:
            return self.tree_minimum(x.right)
        y = x.p
        while y is not None and x is y.right:
            x, y = y, y.p
        return y

    def tree_predecessor(self, x):
        """中序前驱：对称操作。"""
        if x.left is not None:
            return self.tree_maximum(x.left)
        y = x.p
        while y is not None and x is y.left:
            x, y = y, y.p
        return y

    def inorder(self):
        acc = []
        def walk(n):
            if n:
                walk(n.left); acc.append(n.key); walk(n.right)
        walk(self.root)
        return acc


def build_sample_tree():
    """复用图 12.2 的树：15,6,3,2,4,7,13,9,18,17,20"""
    bst = BinarySearchTree()
    for k in (15, 6, 3, 2, 4, 7, 13, 9, 18, 17, 20):
        bst.insert(k)
    return bst


def demo():
    print("=" * 60)
    print("12.2 BST 查询（教科书图 12.2 的树）")
    bst = build_sample_tree()
    print("中序:", bst.inorder())
    print()
    print("– SEARCH")
    print("  search(13):", bst.tree_search(13).key, "| iterative_search(13):", bst.iterative_tree_search(13).key)
    print("  search(16):", bst.tree_search(16), "（None = 不存在）")
    print()
    print("– MINIMUM / MAXIMUM")
    print("  min:", bst.tree_minimum().key, " max:", bst.tree_maximum().key)
    print()
    print("– SUCCESSOR / PREDECESSOR")
    x13 = bst.tree_search(13)
    s = bst.tree_successor(x13)
    print(f"  successor(13) = {s.key if s else None}  ← 13 有右子树(9?不,右=13的右子树…图中13无右) → 上溯到 15")

    x15 = bst.tree_search(15)
    s15 = bst.tree_successor(x15)
    print(f"  successor(15) = {s15.key if s15 else None}  ← 15 有右子树 18 → 右子树最小 17")
    x6 = bst.tree_search(6)
    p6 = bst.tree_predecessor(x6)
    print(f"  predecessor(6) = {p6.key if p6 else None}  ← 6 有左子树 3 → 左子树最大 4")
    print()
    print("逐 key 全 successors 链（从 min 开始应得到升序序列）:")
    cur = bst.tree_minimum()
    seq = []
    while cur is not None:
        seq.append(cur.key)
        cur = bst.tree_successor(cur)
    print(" ", seq)


if __name__ == "__main__":
    demo()
