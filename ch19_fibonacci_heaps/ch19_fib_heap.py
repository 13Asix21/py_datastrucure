# -*- coding: utf-8 -*-
"""
第19章 斐波那契堆 —— 19.1~19.3 完整实现
《算法导论（原书第3版）》CLRS

可合并堆操作：INSERT / UNION / MINIMUM / EXTRACT-MIN / DECREASE-KEY / DELETE。
摊还界（19.3）：extract-min O(lg n)，delete O(lg n)，其余 O(1)。

结构要点：
  - 一组"最小堆有序"的多叉树组成的森林，根链成环
  - mark：结点自从成为别人孩子后是否丢失过孩子
  - 级联切割（cascading cut）
"""


class FibNode:
    __slots__ = ("key", "degree", "p", "child", "left", "right", "mark", "payload")

    def __init__(self, key, payload=None):
        self.key = key
        self.degree = 0
        self.p = None
        self.child = None
        self.left = self
        self.right = self
        self.mark = False
        self.payload = payload           # 附载（如图算法的顶点 id），不参与比较


class FibonacciHeap:
    def __init__(self):
        self.min = None
        self.n = 0

    # ---------- 内部：环操作 ----------
    def _add_to_rootlist(self, x):
        """把 x 挂到根环（min 旁）。"""
        if self.min is None:
            self.min = x
            x.left = x.right = x
        else:
            x.left = self.min.left
            x.right = self.min
            x.left.right = x
            x.right.left = x
            if x.key < self.min.key:
                self.min = x

    @staticmethod
    def _remove_from_list(x):
        """从环中摘除 x（保留指针清理给调用方）。"""
        x.left.right = x.right
        x.right.left = x.left

    # ---------- 19.2 可合并堆操作 ----------
    def insert(self, k, payload=None):
        """O(1)"""
        x = FibNode(k, payload)
        self._add_to_rootlist(x)
        self.n += 1
        return x

    def minimum(self):
        return None if self.min is None else self.min.key

    def union(self, other):
        """UNION：两根环拼接。O(1)"""
        if other.min is None:
            return self
        if self.min is None:
            self.min, self.n = other.min, other.n
            other.min, other.n = None, 0
            return self
        # self 尾 ⇄ other 头；other 尾 ⇄ self 头
        self_min, other_min = self.min, other.min
        self_tail, other_tail = self_min.left, other_min.left
        self_tail.right = other_min
        other_min.left = self_tail
        other_tail.right = self_min
        self_min.left = other_tail
        if other_min.key < self_min.key:
            self.min = other_min
        self.n += other.n
        other.min, other.n = None, 0
        return self

    def extract_min(self):
        """EXTRACT-MIN：摘 min，孩子进根环，consolidate。摊还 O(lg n)"""
        z = self._extract_min_node()
        return z.key if z is not None else None

    def _extract_min_node(self):
        """同 extract_min 但返回结点本身（Dijkstra 等需要 payload 的场景）。"""
        z = self.min
        if z is None:
            return None
        # z 的孩子全部进根环
        if z.child is not None:
            children = []
            c = z.child
            while True:
                children.append(c)
                c = c.right
                if c is z.child:
                    break
            for c in children:
                c.p = None
                c.left = c.right = c          # 先断开孩子环再挂
                self._add_to_rootlist(c)
        # 摘除 z
        if z.right is z:
            self.min = None
        else:
            self._remove_from_list(z)
            self.min = z.right
            self._consolidate()
        self.n -= 1
        return z

    def _consolidate(self):
        """合并同度树。"""
        import math
        max_d = int(math.log2(self.n + 1)) * 2 + 4 if self.n else 4
        A = [None] * max(max_d, 8)
        roots = []
        x = self.min
        while True:
            roots.append(x)
            x = x.right
            if x is self.min:
                break
        for w in roots:
            x = w
            d = x.degree
            while d < len(A) and A[d] is not None:
                y = A[d]
                if x is y:
                    A[d] = None
                    continue
                if x.key > y.key:
                    x, y = y, x
                self._fib_heap_link(y, x)
                A[d] = None
                d += 1
            if d >= len(A):
                A += [None] * (d - len(A) + 1)
            A[d] = x
        # 重建根环
        self.min = None
        for x in A:
            if x is not None:
                x.left = x.right = x
                self._add_to_rootlist(x)

    def _fib_heap_link(self, y, x):
        """y 挂成 x 的孩子。"""
        self._remove_from_list(y)
        y.p = x
        y.mark = False
        if x.child is None:
            x.child = y
            y.left = y.right = y
        else:
            y.left = x.child.left
            y.right = x.child
            y.left.right = y
            y.right.left = y
        x.degree += 1

    def decrease_key(self, x, k):
        """DECREASE-KEY。摊还 O(1)"""
        if k > x.key:
            raise ValueError("新 key 必须不大于原 key")
        x.key = k
        y = x.p
        if y is not None and x.key < y.key:
            self._cut(x, y)
            self._cascading_cut(y)
        if x.key < self.min.key:
            self.min = x

    def _cut(self, x, y):
        """把 y 的孩子 x 切回根环。"""
        if x.right is x:
            y.child = None
        else:
            self._remove_from_list(x)
            if y.child is x:
                y.child = x.right
        y.degree -= 1
        x.p = None
        x.mark = False
        x.left = x.right = x
        self._add_to_rootlist(x)

    def _cascading_cut(self, y):
        """级联切割。"""
        z = y.p
        while z is not None:
            if y.mark is False:
                y.mark = True
                break
            self._cut(y, z)
            y, z = z, z.p

    def delete(self, x):
        """DELETE：降到 -inf 再 extract。"""
        self.decrease_key(x, float("-inf"))
        self.extract_min()

    # ---------- 校验 ----------
    def verify(self):
        """校验 CLRS 真实不变量：
        - 堆序（父 ≤ 子）
        - degree 字段与孩子链长度一致
        - 父指针双向正确
        - 结点计数 == n
        - min 指向全局最小
        注意：根环度数允许重复（consolidate 只在 extract-min 时跑）；
        根可以带 mark（extract-min 提升孩子时书里不清 mark，harbor 无害）。
        """
        errs = []
        if self.min is None:
            return (self.n == 0, errs) if self.n == 0 else (False, ["n≠0 但堆空"])
        roots = []
        x = self.min
        while True:
            roots.append(x)
            x = x.right
            if x is self.min:
                break
        count = 0

        def chk_tree(node, is_root):
            nonlocal count
            count += 1
            if node.p is not None and node.key < node.p.key:
                errs.append(f"堆序违反: 子 {node.key} < 父 {node.p.key}")
            kids = []
            if node.child is not None:
                c = node.child
                while True:
                    kids.append(c)
                    c = c.right
                    if c is node.child:
                        break
            if node.degree != len(kids):
                errs.append(f"degree 不符 @ {node.key}: {node.degree}≠{len(kids)}")
            for c in kids:
                if c.p is not node:
                    errs.append(f"父指针不符 @ {c.key}")
                chk_tree(c, False)

        for r in roots:
            chk_tree(r, True)
        if count != self.n:
            errs.append(f"计数 {count} != n {self.n}")
        for r in roots:
            if r.key < self.min.key:
                errs.append(f"min 指针非最小: {r.key} < {self.min.key}")
        return len(errs) == 0, errs


def demo():
    print("=" * 60)
    print("19 斐波那契堆：核心操作全流程")
    import random
    random.seed(9)

    # 1) insert + extract-min 对拍 sorted
    h = FibonacciHeap()
    keys = random.sample(range(1000), 50)
    for k in keys:
        h.insert(k)
    ok, errs = h.verify()
    print(f"insert 50 个 → 校验 {'✓' if ok else '✗ ' + str(errs[:2])}")
    extracted = [h.extract_min() for _ in range(50)]
    print("extract-min 升序对拍:", "✓" if extracted == sorted(keys) else "✗")

    # 2) union
    h1, h2 = FibonacciHeap(), FibonacciHeap()
    for k in (5, 3, 8):
        h1.insert(k)
    for k in (4, 7, 1):
        h2.insert(k)
    h1.union(h2)
    ok, _ = h1.verify()
    merged = []
    while h1.minimum() is not None:
        merged.append(h1.extract_min())
    expect = sorted([5, 3, 8, 4, 7, 1])
    print(f"union 后校验 {'✓' if ok else '✗'}；弹出序列 == 期望 {expect}:",
          "✓" if merged == expect else "✗")

    # 3) decrease-key（触发 cut）
    h = FibonacciHeap()
    nodes = [h.insert(k) for k in range(10, 0, -1)]
    for _ in range(3):
        h.extract_min()                       # 触发 consolidate，形成非平凡树
    deep = h.insert(99)
    h.decrease_key(deep, 2)                   # 触发 cut
    ok, errs = h.verify()
    print("decrease-key 后校验:", "✓" if ok else "✗ " + str(errs[:2]))

    # 4) delete
    h = FibonacciHeap()
    ns = {k: h.insert(k) for k in (50, 40, 30, 20, 10)}
    h.delete(ns[30])
    remaining = []
    while h.minimum() is not None:
        remaining.append(h.extract_min())
    print("delete(30) 后弹出:", remaining, "== [10, 20, 40, 50]:",
          "✓" if remaining == [10, 20, 40, 50] else "✗")

    # 5) 大混战：随机 insert / extract / delete / decrease-key，全程校验
    random.seed(2026)
    h = FibonacciHeap()
    live = {}          # key -> node
    bad = 0
    for step in range(300):
        r = random.random()
        if r < 0.5:
            k = random.randrange(10000)
            if k not in live:
                live[k] = h.insert(k)
        elif r < 0.75 and live:
            k = random.choice(list(live))
            node = live.pop(k)
            h.delete(node)
        elif live:
            k = random.choice(list(live))
            node = live.pop(k)
            new_k = k - random.randrange(1, 100)
            if new_k not in live:
                h.decrease_key(node, new_k)     # node 仍在堆里，只是 key 变了
                live[new_k] = node
            else:
                h.delete(node)          # 撞 key 就直接删，保持字典纯净
        if step % 25 == 0:
            ok, errs = h.verify()
            if not ok:
                bad += 1
                print(f"  ✗ step {step}: {errs[:2]}")
    ok, _ = h.verify()
    print(f"混战 300 步完成；最终校验 {'✓' if ok else '✗'}，中途破坏 {bad} 次")


if __name__ == "__main__":
    demo()
