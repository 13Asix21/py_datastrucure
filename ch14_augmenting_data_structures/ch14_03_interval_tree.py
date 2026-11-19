# -*- coding: utf-8 -*-
"""
第14章 数据结构的扩张 —— 14.3 区间树
《算法导论（原书第3版）》CLRS

红黑树 + max 字段：x.max = max(x.int.high,
                             x.left.max, x.right.max)
支持 INTERVAL-SEARCH：找任一与给定区间重叠的结点。O(lg n)
（找"全部"重叠需另做遍历。）

重叠定义：a ⊛ b ⇔ a.low ≤ b.high 且 a.low ≤ b.high …
教科书式：i ⊛ j ⇔ i.low ≤ j.high 且 j.low ≤ i.high
"""


RED, BLACK = "R", "B"


class IntervalNode:
    __slots__ = ("interval", "key", "color", "max", "p", "left", "right")

    def __init__(self, low, high, color=RED):
        self.interval = (low, high)
        self.key = low               # 按 low 排序做 BST key
        self.color = color
        self.max = high
        self.p = None
        self.left = None
        self.right = None


class IntervalTree:
    def __init__(self):
        self.nil = IntervalNode(None, None, BLACK)
        self.nil.max = float("-inf")
        self.nil.left = self.nil.right = self.nil.p = self.nil
        self.root = self.nil

    # ---------- 基础红黑底座（带 max 维护）----------
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
        self._recalc_max(x);            # 先算下沉的 x
        self._recalc_max(y)

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
        self._recalc_max(y)
        self._recalc_max(x)

    def _recalc_max(self, x):
        if x is not self.nil:
            x.max = max(x.interval[1],
                        x.left.max if x.left is not self.nil else float("-inf"),
                        x.right.max if x.right is not self.nil else float("-inf"))

    def insert(self, low, high):
        """插入区间 [low, high]。O(lg n)"""
        assert low <= high, "区间必须 low ≤ high"
        z = IntervalNode(low, high, RED)
        z.left = z.right = self.nil
        z.max = high
        y, x = self.nil, self.root
        while x is not self.nil:
            y = x
            if z.max > x.max:           # ← 14.3 扩张：沿路径抬 max
                x.max = z.max
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

    # ---------- 14.3 区间查找 ----------
    def interval_search(self, low, high):
        """INTERVAL-SEARCH：任找一重叠区间。O(lg n)"""
        x = self.root
        while x is not self.nil and not (low <= x.interval[1] and x.interval[0] <= high):
            # 不重叠：若左子树 max ≥ low 才可能重叠 → 往左；否则右
            if x.left is not self.nil and x.left.max >= low:
                x = x.left
            else:
                x = x.right
        return None if x is self.nil else x

    def search_all_overlaps(self, low, high):
        """找全部重叠（教科书练习：O(k lg n)）。"""
        out = []
        def walk(x):
            if x is self.nil:
                return
            if low <= x.interval[1] and x.interval[0] <= high:
                out.append(x.interval)
            if x.left is not self.nil and x.left.max >= low:
                walk(x.left)
            if x.interval[0] <= high:
                walk(x.right)
        walk(self.root)
        return out

    # ---------- 校验 ----------
    def verify_max(self):
        errs = []
        def chk(x):
            if x is self.nil:
                return float("-inf")
            lm, rm = chk(x.left), chk(x.right)
            expect = max(x.interval[1], lm, rm)
            if x.max != expect:
                errs.append(f"max 错 @ {x.interval}: 存{x.max} 应{expect}")
                x.max = expect
            return x.max
        chk(self.root)
        return len(errs) == 0, errs

    def inorder(self, x=None, acc=None):
        if acc is None:
            acc, x = [], self.root
        if x is not self.nil:
            self.inorder(x.left, acc)
            acc.append((x.interval, x.max))
            self.inorder(x.right, acc)
        return acc


def demo():
    print("=" * 60)
    print("14.3 区间树 INTERVAL-SEARCH")
    t = IntervalTree()
    intervals = [(16, 21), (8, 9), (25, 30), (5, 8), (15, 23), (17, 19), (26, 26), (0, 3), (6, 10), (19, 20)]
    for lo, hi in intervals:
        t.insert(lo, hi)
    ok, errs = t.verify_max()
    print(f"插入 {len(intervals)} 个区间，max 维护 {'✓' if ok else '✗'}")
    print("中序(按 low):", [(iv, m) for iv, m in t.inorder()])

    print()
    print("单点/区间查询：")
    queries = [(14, 16), (22, 25), (24, 24), (3, 4), (18, 18), (100, 200)]
    all_ok = True
    for lo, hi in queries:
        hit = t.interval_search(lo, hi)
        all_overlaps = t.search_all_overlaps(lo, hi)
        hit_iv = hit.interval if hit else None
        # 单一结果必须出现在全量结果里
        consistent = (hit_iv is None and not all_overlaps) or (hit_iv in all_overlaps)
        all_ok &= consistent
        print(f"  查询 [{lo},{hi}] → 单hits: {hit_iv} | 全部重叠: {sorted(all_overlaps)}  {'✓' if consistent else '✗'}")
    print()
    print("整体一致性:", "✓" if all_ok else "✗")


if __name__ == "__main__":
    demo()
