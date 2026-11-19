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

    # ---------- 14.1 删除（练习 14.1-3/14.1-4：size 与红黑修复并行维护）----------
    def rb_transplant(self, u, v):
        """RB-TRANSPLANT + 沿 u 的祖先链 size-1（v 顶上来不影响祖先 count，
        但 u 消失使所有真祖先 -1；u 子树内部的 size 不变，v 子树自带）。"""
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

    def delete(self, k):
        """OS-DELETE：红黑删除 + size 全链修正。O(lg n)

        size 账本（物理上消失的结点只有 z 一个，y 只是挪位）：
        · z 的每个真祖先：其子树 -1 → 沿 z.p 上行 -1。
        · c2 时 y 从 z 的右子树挪出：z 右子树内 y 的原父链每结点子树 -1
          （c1 时 y 就是 z.right，右子树内无中间链）。
        · y 换位后 size 重算：y.left.size + y.right.size + 1（孩子接好后）。
        颜色：y 必须接管 z 的颜色（y_original_color 在接管前记录，供 fixup 判断）。
        """
        z = self._search(k)
        if z is self.nil:
            return False

        y = z
        y_original_color = y.color
        if z.left is self.nil:
            x = z.right
            self._dec_up(z.p)                        # z 真祖先 -1
            self.rb_transplant(z, z.right)
        elif z.right is self.nil:
            x = z.left
            self._dec_up(z.p)
            self.rb_transplant(z, z.left)
        else:
            y = self.tree_minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.p is z:
                # c1：y 紧贴 z。先写 x.p（nil 父指针要在 transplant 覆盖前置位）
                x.p = y
                # size：z 真祖先 -1；y 顶位后子树少 z 一个结点
                self._dec_up(z.p)
            else:
                # c2：y 深处。先把 y 从 z 右子树摘出：
                # z 右子树内 y 的原父链（y.p 到 z.right 之下）每结点 -1
                w = y.p
                while w is not z:
                    w.size -= 1
                    w = w.p
                self.rb_transplant(y, y.right)   # nil.p 自动写为 y 的原父（教科书顺序）
                y.right = z.right
                y.right.p = y
                # z 真祖先 -1（z 消失）
                self._dec_up(z.p)
            self.rb_transplant(z, y)
            y.left = z.left
            y.left.p = y
            y.size = y.left.size + y.right.size + 1   # 换位后重算
            y.color = z.color                          # 接管 z 颜色（fixup 判据用的是接管前记录）
        if y_original_color == BLACK:
            self._delete_fixup(x)
        return True

    def _dec_up(self, p):
        """从 p 起沿父链到根：每结点 size -= 1。p 为 nil 哨兵时自然停（根的父是 nil）。"""
        while p is not self.nil:
            p.size -= 1
            p = p.p

    def _delete_fixup(self, x):
        """红黑修复（NIL 哨兵版，同 ch13 demo_utils），旋转已自带 size 维护。"""
        while x is not self.root and x.color == BLACK:
            if x is x.p.left:
                w = x.p.right
                if w.color == RED:
                    w.color = BLACK
                    x.p.color = RED
                    self.left_rotate(x.p)
                    w = x.p.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.p
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self.right_rotate(w)
                        w = x.p.right
                    w.color = x.p.color
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

    def verify_rb(self):
        """红黑性质 2/4/5 校验（size 文件自带的 verify_sizes 只管扩张字段）。"""
        errs = []
        if self.root is not self.nil:
            if self.root.color != BLACK:
                errs.append("性质2: 根不是黑")

            def bh(x):
                if x is self.nil:
                    return 1
                lbh, rbh = bh(x.left), bh(x.right)
                if lbh != rbh:
                    errs.append(f"性质5: key={x.key} 黑高不等")
                if x.color == RED and (x.left.color == RED or x.right.color == RED):
                    errs.append(f"性质4: 红结点 {x.key} 有红孩子")
                return lbh + (1 if x.color == BLACK else 0)

            bh(self.root)
        return len(errs) == 0, errs


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
    print(f"插入 40 个 key，size 全程维护 {'✓' if ok else '✗ ' + str(errs[:2])}")
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


def demo_delete():
    """14.1 删除：乱序全删 + 混合操作，size 与红黑性质双校验。"""
    print("=" * 60)
    print("14.1 OS-DELETE：乱序全删 + 5000 次插删混战")
    import random
    random.seed(77)
    t = OSTree()
    keys = random.sample(range(10_000), 300)
    for k in keys:
        t.insert(k)
    # 乱序全删
    order = keys[:]
    random.shuffle(order)
    bad_size = bad_rb = 0
    for k in order:
        assert t.delete(k), f"delete({k}) 失败"
        ok1, e1 = t.verify_sizes()
        ok2, e2 = t.verify_rb()
        if not ok1:
            bad_size += 1
            if bad_size == 1:
                print(f"  ✗ size: {e1[:2]}")
        if not ok2:
            bad_rb += 1
            if bad_rb == 1:
                print(f"  ✗ 红黑: {e2[:2]}")
    remain = [k for k, _ in t.inorder()]
    print(f"  乱序删除 300 个：size 破坏 {bad_size} 次 | 红黑破坏 {bad_rb} 次 | 剩余 {len(remain)}",
          "✓" if bad_size == bad_rb == 0 and not remain else "✗")
    # 混战：删后再插，rank/select 随时抽验
    random.seed(88)
    live = set()
    for step in range(5000):
        k = random.randrange(2000)
        if k in live and random.random() < 0.5:
            t.delete(k)
            live.discard(k)
        elif k not in live:
            t.insert(k)
            live.add(k)
        if step % 500 == 0:
            ok1, _ = t.verify_sizes()
            ok2, _ = t.verify_rb()
            if not (ok1 and ok2):
                print(f"  ✗ step {step}: size_ok={ok1} rb_ok={ok2}")
                break
    else:
        # 终局：OS-RANK/SELECT 与排序模型全量对拍
        ref = sorted(live)
        rank_ok = all(t.os_rank(k) == i + 1 for i, k in enumerate(ref))
        sel_ok = all(t.os_select(t.root, i + 1).key == k for i, k in enumerate(ref))
        print(f"  混战 5000 步后：rank 全量 {len(ref)} 项 {'✓' if rank_ok else '✗'} | select 全量 {'✓' if sel_ok else '✗'}")


if __name__ == "__main__":
    demo()
    demo_delete()
