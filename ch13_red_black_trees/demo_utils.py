# -*- coding: utf-8 -*-
"""
第13章红黑树公共件（demo_utils）
《算法导论（原书第3版）》CLRS 13.1~13.4

采用教科书原生的 NIL 哨兵实现：
  - 所有空孩子/空父指针都指向真实结点 self.nil（黑色，key=None）
  - RB-TRANSPLANT 中 v.p = u.p 是无条件赋值（包括 v 是 nil 的情形），
    这让删除修复时 nil 也带着 parent 指针 —— 这正是哨兵版的意义。

ch13_01（旋转/插入演示）、ch13_02（删除演示）从这里导入。
"""


RED = "R"
BLACK = "B"


class RBNode:
    __slots__ = ("key", "color", "p", "left", "right")

    def __init__(self, key, color=RED):
        self.key = key
        self.color = color
        self.p = None
        self.left = None
        self.right = None


class RedBlackTree:
    def __init__(self):
        self.nil = RBNode(None, BLACK)   # 哨兵：黑色，key=None
        self.nil.p = self.nil
        self.nil.left = self.nil
        self.nil.right = self.nil
        self.root = self.nil

    # ================ 13.2 旋转 ================
    def left_rotate(self, x):
        """LEFT-ROTATE(T, x)
            x                y
           / \\             / \\
          a   y    ==>    x   c
             / \\         / \\
            b   c       a   b
        """
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

    def right_rotate(self, y):
        """RIGHT-ROTATE：镜像。"""
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

    # ================ 13.3 插入 ================
    def insert(self, k):
        """RB-INSERT + RB-INSERT-FIXUP。O(lg n)"""
        z = RBNode(k, RED)
        z.left = z.right = self.nil
        y, x = self.nil, self.root
        while x is not self.nil:
            y = x
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
        """RB-INSERT-FIXUP：3 case × 左右镜像。"""
        while z.p.color == RED:
            if z.p is z.p.p.left:
                y = z.p.p.right                 # 叔叔（可为 nil=黑）
                if y.color == RED:              # case 1
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z is z.p.right:          # case 2（三角）
                        z = z.p
                        self.left_rotate(z)
                    z.p.color = BLACK           # case 3（直线）
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

    # ================ 13.4 删除 ================
    def rb_transplant(self, u, v):
        """RB-TRANSPLANT。注意：v.p = u.p 无条件执行（v==nil 时也写），
        好让后续 fixup 通过 nil.p 找到位置。"""
        if u.p is self.nil:
            self.root = v
        elif u is u.p.left:
            u.p.left = v
        else:
            u.p.right = v
        v.p = u.p

    def tree_minimum(self, x):
        while x.left is not self.nil:
            x = x.left
        return x

    def search(self, k):
        x = self.root
        while x is not self.nil and x.key != k:
            x = x.left if k < x.key else x.right
        return x

    def delete(self, k):
        """RB-DELETE(T, z)。O(lg n)。返回是否删除成功。"""
        z = self.search(k)
        if z is self.nil:
            return False
        y = z
        y_original_color = y.color
        if z.left is self.nil:
            x = z.right
            self.rb_transplant(z, z.right)
        elif z.right is self.nil:
            x = z.left
            self.rb_transplant(z, z.left)
        else:
            y = self.tree_minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.p is z:
                x.p = y
            else:
                self.rb_transplant(y, y.right)
                y.right = z.right
                y.right.p = y
            self.rb_transplant(z, y)
            y.left = z.left
            y.left.p = y
            y.color = z.color
        if y_original_color == BLACK:
            self._delete_fixup(x)
        return True

    def _delete_fixup(self, x):
        """RB-DELETE-FIXUP：4 case × 左右镜像。
        x 可以是 self.nil（哨兵带着 .p 参与循环，无需特判）。"""
        while x is not self.root and x.color == BLACK:
            if x is x.p.left:
                w = x.p.right                    # 兄弟
                if w.color == RED:               # case 1：兄红
                    w.color = BLACK
                    x.p.color = RED
                    self.left_rotate(x.p)
                    w = x.p.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED                # case 2：兄黑 + 两侄黑
                    x = x.p
                else:
                    if w.right.color == BLACK:   # case 3：远侄黑、近侄红
                        w.left.color = BLACK
                        w.color = RED
                        self.right_rotate(w)
                        w = x.p.right
                    w.color = x.p.color          # case 4：远侄红
                    x.p.color = BLACK
                    w.right.color = BLACK
                    self.left_rotate(x.p)
                    x = self.root
            else:
                w = x.p.left
                if w.color == RED:
                    w.color = BLACK
                    x.p.color = RED
                    self.right_rotate(x.p)
                    w = x.p.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.p
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self.left_rotate(w)
                        w = x.p.left
                    w.color = x.p.color
                    x.p.color = BLACK
                    w.left.color = BLACK
                    self.right_rotate(x.p)
                    x = self.root
        x.color = BLACK

    # ================ 校验与输出 ================
    def verify(self):
        """校验性质 2/4/5（1/3 由哨兵构造保证）。"""
        errs = []
        if self.root is not self.nil:
            if self.root.color != BLACK:
                errs.append("性质2: 根不是黑色")

            def bh(x):
                if x is self.nil:
                    return 1                    # 叶(nil)黑高 1
                lbh, rbh = bh(x.left), bh(x.right)
                if lbh != rbh:
                    errs.append(f"性质5: key={x.key} 左右黑高不等 {lbh}≠{rbh}")
                if x.color == RED:
                    if x.left.color == RED or x.right.color == RED:
                        errs.append(f"性质4: 红结点 {x.key} 有红孩子")
                return lbh + (1 if x.color == BLACK else 0)

            bh(self.root)
        return len(errs) == 0, errs

    def inorder(self, x=None, acc=None):
        if acc is None:
            acc, x = [], self.root
        if x is not self.nil:
            self.inorder(x.left, acc)
            acc.append((x.key, x.color))
            self.inorder(x.right, acc)
        return acc

    def height(self, x=None):
        if x is None:
            x = self.root
        if x is self.nil:
            return 0
        return 1 + max(self.height(x.left), self.height(x.right))

    def black_height(self):
        """根的黑高（不含根？含根 —— 按 CLRS 定义 bh = 路径上黑结点数，含根）。"""
        x = self.root
        cnt = 0
        while x is not self.nil:
            if x.color == BLACK:
                cnt += 1
            x = x.left                            # 任一路径即可（性质5 保证相等）
        return cnt + 1                            # 补上叶 nil
