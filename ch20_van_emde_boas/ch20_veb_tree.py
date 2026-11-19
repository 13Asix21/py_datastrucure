# -*- coding: utf-8 -*-
"""
第20章 van Emde Boas 树 —— 20.1~20.3
《算法导论（原书第3版）》CLRS

递归结构(proto-vEB) → 真正的 van Emde Boas 树。
关键：宇宙大小 u = 2^(2^k)，位折叠递归降到 O(lg lg u / lg 2) = O(lg lg u)。

本实现是不带 cluster 数组捷径的"纯"递归版（20.2 proto-vEB → 20.3 vEB），
操作：MEMBER / INSERT / MINIMUM / MAXIMUM / SUCCESSOR / PREDECESSOR / DELETE。
Python 递归实现，u ≤ 2^16 做演示（u=2^32 层深只有 5 层，但内存是问题）。

注：教科书 20.3 的 vEB 树用 summary + cluster[] + min/max 冗余优化，本实现保真。
"""


import math


class VEBTree:
    """20.3 van Emde Boas 树（递归两路拆分 u → √u × √u）。"""

    def __init__(self, u):
        assert u >= 2 and (u & (u - 1)) == 0, "u 必须是 2 的幂"
        self.u = u
        self.min = None                   # None = 空
        self.max = None
        if u > 2:
            self.sqrt_half = int(math.isqrt(u))  # u = 2^k → √u
            # high(x) = x // √u（簇编号），low(x) = x % √u（簇内偏移）
            self.cluster = {}             # 懒建：簇号 → VEBTree(√u)
            self.summary = VEBTree(self.sqrt_half)

    # —— 拆坐标 ——
    def _high(self, x):
        return x // self.sqrt_half

    def _low(self, x):
        return x % self.sqrt_half

    def _index(self, high, low):
        return high * self.sqrt_half + low

    def _get_cluster(self, c):
        if c not in self.cluster:
            self.cluster[c] = VEBTree(self.sqrt_half)
        return self.cluster[c]

    # —— 20.3.2 操作 ——
    def member(self, x):
        """MEMBER。O(lg lg u)"""
        if x == self.min or x == self.max:
            return True
        if self.u == 2:
            return False
        c = self._get_cluster(self._high(x))
        return c.member(self._low(x))

    def insert(self, x):
        """INSERT（教科书版：懒 min，不递归到空簇）。O(lg lg u)
        注：CLRS 假定元素互异。此处加 member 护栏防止重复插入
        产生双份拷贝（min 的懒存 + 簇内各一份），破坏结构。"""
        if self.member(x):
            return
        if self.min is None:
            self.min = self.max = x
            return
        if x < self.min:
            x, self.min = self.min, x      # 原 min 下放簇内
        if self.u == 2:
            self.max = max(self.min, x)  # 直接算
            return
        h = self._high(x)
        c = self._get_cluster(h)
        if c.min is None:
            self.summary.insert(h)        # 该簇首个元素
            c.insert(self._low(x))
        else:
            c.insert(self._low(x))
        if x > self.max:
            self.max = x

    def minimum(self):
        return self.min

    def maximum(self):
        return self.max

    def successor(self, x):
        """SUCCESSOR(x)：大于 x 的最小元素。O(lg lg u)"""
        if self.u == 2:
            if x == 0 and self.max == 1:
                return 1
            return None
        if self.min is not None and x < self.min:
            return self.min
        # 簇内找后继
        h, l = self._high(x), self._low(x)
        c = self.cluster.get(h)
        if c is not None and c.max is not None and l < c.max:
            offset = c.successor(l)
            return self._index(h, offset)
        # 下一非空簇
        next_cluster = self.summary.successor(h)
        if next_cluster is not None:
            c2 = self.cluster[next_cluster]
            return self._index(next_cluster, c2.min)
        return None

    def predecessor(self, x):
        if self.u == 2:
            if x == 1 and self.min == 0:
                return 0
            return None
        if self.max is not None and x > self.max:
            return self.max
        h, l = self._high(x), self._low(x)
        c = self.cluster.get(h)
        if c is not None and c.min is not None and l > c.min:
            offset = c.predecessor(l)
            return self._index(h, offset)
        prev_cluster = self.summary.predecessor(h)
        if prev_cluster is not None:
            c2 = self.cluster[prev_cluster]
            return self._index(prev_cluster, c2.max)
        # min 出现在 x 之前的特判：min 不在任何簇里
        if self.min is not None and self.min < x:
            return self.min
        return None

    def delete(self, x):
        """DELETE。O(lg lg u)
        注意：CLRS 的 vEB-DELETE 假定 x ∈ 树。本实现加成员护栏，
        使其成为"全集字典语义"（删不存在的 key 返回 False）。"""
        if self.min is None or x < self.min or x > self.max:
            return False
        if not self.member(x):
            return False
        if self.min == self.max == x and x == self.min:
            # 唯一元素
            self.min = self.max = None
            return True
        if self.u == 2:
            # 树里此时有 min≠max 两元素（{0,1}），删 x 后只剩另一个
            other = 1 - x
            self.min = self.max = other
            return True
        if x == self.min:
            # 用第一个非空簇的 min 顶替 min
            first = self.summary.minimum()
            if first is None:
                self.min = self.max = None
                return True
            c = self.cluster[first]
            x = self._index(first, c.min)
            self.min = x
            c.delete(c.min)
            if c.min is None:
                self.summary.delete(first)
        else:
            h, l = self._high(x), self._low(x)
            c = self.cluster.get(h)
            if c is None or c.min is None:
                return False                     # 簇不存在/空 → x 不在树中
            c.delete(l)
            if c.min is None:
                self.summary.delete(h)
        # 更新 max
        if self.max == x:
            if self.min is not None and self.min == self.max:
                pass
            summ_max = self.summary.maximum()
            if summ_max is None:
                self.max = self.min
            else:
                self.max = self._index(summ_max, self.cluster[summ_max].max)
        return True


def demo():
    print("=" * 60)
    print("20.3 van Emde Boas 树（u=256）")
    t = VEBTree(256)
    keys = [100, 3, 250, 7, 42, 255, 0, 128, 199]
    for k in keys:
        t.insert(k)
    print("插入:", sorted(keys))
    print("MIN:", t.minimum(), " MAX:", t.maximum())
    for q in (3, 42, 250, 128):
        print(f"MEMBER({q}):", t.member(q))
    for q in (5, 100, 200, 255):
        s = t.successor(q)
        p = t.predecessor(q)
        print(f"SUCCESSOR({q}) = {s}   PREDECESSOR({q}) = {p}")
    print()
    print("删除测试：")
    t.delete(100)
    t.delete(0)
    ok_mid = t.member(100)
    print("delete(100), delete(0) → member(100):", ok_mid, "（应 False）")
    remaining = []
    x = t.minimum()
    while x is not None:
        remaining.append(x)
        x = t.successor(x)
    expect = sorted(set(keys) - {100, 0})
    print("按 successor 链遍历剩余:", remaining, "== 期望:", expect, ":", "✓" if remaining == expect else "✗")
    # 全删
    for k in expect:
        t.delete(k)
    print("全删后 MIN/MAX:", t.minimum(), t.maximum(), "（应 None None）")


def demo_stress():
    print("=" * 60)
    print("压力对拍：vEB(u=65536) vs Python set（随机 2000 次操作）")
    import random
    random.seed(77)
    t = VEBTree(65536)
    s = set()
    for _ in range(2000):
        op = random.random()
        x = random.randrange(65536)
        if op < 0.6:
            t.insert(x)
            s.add(x)
        else:
            r1 = t.delete(x)
            r2 = x in s
            if r2:
                s.discard(x)
            if r1 != r2:
                print(f"  ✗ delete({x}) 返回 {r1}，集合说 {r2}")
                return
        if random.random() < 0.05:
            # 抽查 successor 与暴力法对拍
            q = random.randrange(65536)
            expect = min([v for v in s if v > q], default=None)
            got = t.successor(q)
            if got != expect:
                print(f"  ✗ successor({q}) = {got}，应为 {expect}")
                return
    print("对拍完成：insert/delete/successor 全一致 ✓")
    print(f"最终 vEB 内元素（set 对拍）: {len(s)} 个")


if __name__ == "__main__":
    demo()
    demo_stress()
