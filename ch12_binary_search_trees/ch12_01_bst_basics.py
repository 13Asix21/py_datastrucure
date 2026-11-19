# -*- coding: utf-8 -*-
"""
第12章 二叉搜索树 —— 12.1 什么是二叉搜索树 + 中序遍历
《算法导论（原书第3版）》CLRS

BST 性质：对任何结点 x，
    x.left 子树所有 key ≤ x.key ≤ x.right 子树所有 key
推论：中序遍历（inorder walk）输出升序序列 —— O(n)。
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

    # ---------- 12.1 遍历 ----------
    def inorder_tree_walk(self, x=None, acc=None):
        """INORDER-TREE-WALK：升序输出。O(n)"""
        if acc is None:
            acc, x = [], self.root
        if x is not None:
            self.inorder_tree_walk(x.left, acc)
            acc.append(x.key)
            self.inorder_tree_walk(x.right, acc)
        return acc

    def preorder_walk(self, x=None, acc=None):
        if acc is None:
            acc, x = [], self.root
        if x is not None:
            acc.append(x.key)
            self.preorder_walk(x.left, acc)
            self.preorder_walk(x.right, acc)
        return acc

    def postorder_walk(self, x=None, acc=None):
        if acc is None:
            acc, x = [], self.root
        if x is not None:
            self.postorder_walk(x.left, acc)
            self.postorder_walk(x.right, acc)
            acc.append(x.key)
        return acc

    # ---------- 建树用：12.3 的插入，此处先用 ----------
    def insert(self, k):
        """TREE-INSERT（12.3 正式实现见 ch12_03，这里先用于建树）。"""
        return _tree_insert(self, Node(k))

    # ---------- 属性自检 ----------
    def is_bst(self, x=None, lo=None, hi=None):
        """递归验证 BST 性质：key ∈ (lo, hi)。"""
        if x is None:
            if lo is None and hi is None:
                x = self.root
            else:
                return True
        if x is None:
            return True
        if lo is not None and x.key <= lo:
            return False
        if hi is not None and x.key >= hi:
            return False
        return self.is_bst(x.left, lo, x.key) and self.is_bst(x.right, x.key, hi)


def _tree_insert(bst, z):
    """TREE-INSERT：沿树下行找空位挂上。期望 O(h)。"""
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


def build_sample_tree():
    """教科书图 12.1 同款 key 集合：15,6,3,2,4,7,13,9,18,17,20"""
    bst = BinarySearchTree()
    for k in (15, 6, 3, 2, 4, 7, 13, 9, 18, 17, 20):
        bst.insert(k)
    return bst


def demo():
    print("=" * 60)
    print("12.1 二叉搜索树与三种深度优先遍历")
    bst = build_sample_tree()
    print("插入序列: 15 6 3 2 4 7 13 9 18 17 20")
    print("中序遍历(升序):", bst.inorder_tree_walk())
    print("先序遍历      :", bst.preorder_walk())
    print("后序遍历      :", bst.postorder_walk())

    print()
    print("BST 性质自检:", "通过 ✓" if bst.is_bst() else "失败 ✗")
    # 破坏性质演示：手动把 18 的右孩子 key 改成 16（应仍满足右>15? 中序立刻乱序）
    bad = build_sample_tree()
    x18 = bad.root.right          # 18
    x18.key = 5                    # 5 < 15 却在右子树 → 违反性质
    print("把右子树结点 18 改成 5 后自检:", "通过 ✗（检测失败?）" if bad.is_bst() else "失败 → 正确检测出违反 ✓")
    print("改后的中序:", bad.inorder_tree_walk(), "（不再升序）")


if __name__ == "__main__":
    demo()
