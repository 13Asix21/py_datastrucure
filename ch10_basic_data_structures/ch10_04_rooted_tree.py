# -*- coding: utf-8 -*-
"""
第10章 基本数据_structures 基本数据结构 —— 10.4 有根树的表示
《算法导论（原书第3版）》CLRS

无指针约束下的树表示：
1) 二叉树：left/right 双指针
2) 分支无限制的树：left-child / right-sibling 表示法 —— O(1) 访问父结点
       大 O 上界比较：让每个结点存 x.p, x.left-child, x.right-sibling

对比（教科书图 10.9）：
    普通多路树（每结点存所有孩子指针）        left-child/right-sibling
    -------------------------------------------------------------------
    列出全部孩子         O(k)                     O(k)
    判断是否叶           查孩子数组是否空          查 left_child 是否 NULL
    内存                 ∑ children 数组长度       每结点恰 2 个指针
"""


class BinaryNode:
    """教科书 p176 图10.8(a)：二叉结点 = key + p + left + right。"""
    __slots__ = ("key", "p", "left", "right")

    def __init__(self, key):
        self.key = key
        self.p = None
        self.left = None
        self.right = None


class LCRSNode:
    """left-child / right-sibling 结点：
    每个结点只存 3 个指针：p, left_child, right_sibling
    """
    __slots__ = ("key", "p", "left_child", "right_sibling")

    def __init__(self, key):
        self.key = key
        self.p = None
        self.left_child = None
        self.right_sibling = None


class BinaryTree:
    """10.4 二叉树表示（演示用最小实现）。"""

    def __init__(self, root_key):
        self.root = BinaryNode(root_key)

    def add_child(self, parent, key, side):
        child = BinaryNode(key)
        child.p = parent
        if side == "L":
            parent.left = child
        elif side == "R":
            parent.right = child
        else:
            raise ValueError("side 必须是 'L' 或 'R'")
        return child

    def inorder(self, x=None, acc=None):
        if acc is None:
            acc = []
            x = self.root
        if x is not None:
            self.inorder(x.left, acc)
            acc.append(x.key)
            self.inorder(x.right, acc)
        return acc


class LCRSTree:
    """left-child / right-sibling 多叉树。"""

    def __init__(self, root_key):
        self.root = LCRSNode(root_key)

    def add_child(self, parent, key):
        """新孩子总是接到孩子链末尾。"""
        c = LCRSNode(key)
        c.p = parent
        if parent.left_child is None:
            parent.left_child = c
        else:
            cur = parent.left_child
            while cur.right_sibling is not None:
                cur = cur.right_sibling
            cur.right_sibling = c
        return c

    def children(self, x):
        out = []
        c = x.left_child
        while c is not None:
            out.append(c)
            c = c.right_sibling
        return out

    def print_tree(self):
        def dump(x, indent=0):
            print("  " * indent + str(x.key))
            for c in self.children(x):
                dump(c, indent + 1)
        dump(self.root)


if __name__ == "__main__":
    print("=" * 60)
    print("10.4 二叉树表示：left/right 指针")
    bt = BinaryTree("A")
    b = bt.add_child(bt.root, "B", "L")
    c = bt.add_child(bt.root, "C", "R")
    bt.add_child(b, "D", "L")
    bt.add_child(b, "E", "R")
    bt.add_child(c, "F", "L")
    print("中序遍历:", bt.inorder())
    print("结点 B 的父指针指向:", b.p.key)

    print("=" * 60)
    print("10.4 分支无限制的树：left-child / right-sibling 表示")
    t = LCRSTree("A")
    b = t.add_child(t.root, "B")
    c = t.add_child(t.root, "C")
    d = t.add_child(t.root, "D")
    e = t.add_child(b, "E")
    b2 = t.add_child(b, "F")
    g = t.add_child(c, "G")
    print("整树结构:")
    t.print_tree()
    print("A 的所有孩子:", [n.key for n in t.children(t.root)])
    print("B 的所有孩子:", [n.key for n in t.children(b)])
    print("F 的父指针:", b2.p.key, "（O(1) 访问）")
