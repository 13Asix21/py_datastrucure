# -*- coding: utf-8 -*-
"""
第21章 用于不相交集合的数据结构 —— 21.1~21.4
《算法导论（原书第3版）》CLRS

两种实现：
  A) 链表表示（21.2）：每集合一条双向链表 + 表头对象
  B) 不相交集合森林（21.3）：带按秩合并 + 路径压缩的父指针森林
     → UNION / FIND 均摊 O(α(n))，α 为反阿克曼函数（≤4 直到 n<16^16）

应用演示：无向图连通分量 + Kruskal 最小生成树中的环检测。
"""


# ============================================================
# A) 链表表示（21.2）
# ============================================================
class ListSet:
    """链表版不相交集。每成员存 set_obj / next / prev。"""
    __slots__ = ("key", "set_obj", "next")

    def __init__(self, key):
        self.key = key
        self.set_obj = None
        self.next = None


class SetObject:
    __slots__ = ("head", "tail", "size")

    def __init__(self, node):
        self.head = node
        self.tail = node
        self.size = 1
        node.set_obj = self
        node.next = None


class DisjointSetLinkedList:
    """MAKE-SET / UNION / FIND-SET（加权合并启发式）。"""

    def make_set(self, key):
        return SetObject(ListSet(key))

    def find_set(self, node):
        return node.set_obj

    def union(self, a: SetObject, b: SetObject):
        """UNION：短表接长表尾（合并启发式，权重=长度）。"""
        if a is b:
            return a
        if a.size < b.size:
            a, b = b, a                 # 保证 a 更长
        # 把 b 的每个成员移到 a 尾
        cur = b.head
        while cur is not None:
            nxt = cur.next
            a.tail.next = cur
            cur.set_obj = a
            a.tail = cur
            cur = nxt
        a.size += b.size
        return a

    def members(self, s: SetObject):
        out = []
        cur = s.head
        while cur is not None:
            out.append(cur.key)
            cur = cur.next
        return out


# ============================================================
# B) 不相交集合森林（21.3）—— 教科书主推
# ============================================================
class ForestNode:
    __slots__ = ("key", "p", "rank")

    def __init__(self, key):
        self.key = key
        self.p = self
        self.rank = 0


class DisjointSetForest:
    """MAKE-SET / UNION（按秩合并）/ FIND-SET（路径压缩）。
    摊还 O(α(n))。"""
    find_count = 0          # 演示用：统计 FIND 遍历深度

    def make_set(self, key):
        return ForestNode(key)

    def union(self, x: ForestNode, y: ForestNode):
        """UNION：按秩合并。"""
        rx, ry = self.find_set(x), self.find_set(y)
        if rx is ry:
            return rx
        self._link(rx, ry)
        return rx if rx.p is rx else ry

    def _link(self, x, y):
        """LINK：秩大的当根。"""
        if x.rank > y.rank:
            y.p = x
        else:
            x.p = y
            if x.rank == y.rank:
                y.rank += 1

    def find_set(self, x):
        """FIND-SET + 路径压缩（两趟法：先找根，再重指父）。"""
        root = x
        depth = 0
        while root.p is not root:
            root = root.p
            depth += 1
        DisjointSetForest.find_count += depth
        # 压缩
        while x.p is not root:
            x.p, x = root, x.p
        return root


# ============================================================
# 应用：连通分量 / Kruskal 环检测
# ============================================================
def demo_connected_components():
    print("=" * 60)
    print("21.1(应用) 无向图连通分量（顶点 a~i，CLRS 图21.1 同款）")
    # 教科书例子：边集
    edges = [("b", "d"), ("e", "g"), ("a", "c"), ("h", "i"),
             ("a", "b"), ("e", "f"), ("b", "c")]
    verts = "abcdefghi"
    dsu = DisjointSetForest()
    nodes = {v: dsu.make_set(v) for v in verts}
    for u, v in edges:
        dsu.union(nodes[u], nodes[v])
    # 分组
    groups = {}
    for v in verts:
        root = dsu.find_set(nodes[v])
        groups.setdefault(root.key, []).append(v)
    print("边:", edges)
    print("连通分量:", sorted(groups.values()))

    # 再动态加边 d f → 应合并成 7 个顶点一组
    dsu.union(nodes["d"], nodes["f"])
    groups = {}
    for v in verts:
        root = dsu.find_set(nodes[v])
        groups.setdefault(root.key, []).append(v)
    print("加边 (d,f) 后:", sorted(groups.values()))
    expect = [["a", "b", "c", "d", "e", "f", "g"], ["h", "i"]]
    ok = sorted(sorted(g) for g in groups.values()) == expect
    print("与期望对拍:", "✓" if ok else "✗", expect)


def demo_kruskal_cycle():
    print("=" * 60)
    print("21.1(应用) Kruskal 环检测")
    # 无向有权图（顶点 1..7）
    weighted_edges = [
        (7, "A", "B"), (5, "A", "D"), (7, "B", "D"), (9, "B", "C"),
        (8, "B", "E"), (5, "C", "E"), (7, "D", "E"), (15, "D", "F"),
        (6, "E", "F"), (8, "E", "G"), (9, "F", "G"), (11, "B", "A"),
    ]
    # 去重无向边
    uniq = {}
    for w, u, v in weighted_edges:
        key = tuple(sorted((u, v)))
        if key not in uniq or w < uniq[key]:
            uniq[key] = w
    dsu = DisjointSetForest()
    nodes = {v: dsu.make_set(v) for v in "ABCDEFG"}
    mst = []
    total = 0
    for (u, v), w in sorted(uniq.items(), key=lambda kv: kv[1]):
        if dsu.find_set(nodes[u]) is not dsu.find_set(nodes[v]):
            dsu.union(nodes[u], nodes[v])
            mst.append((u, v, w))
            total += w
    print("MST 边集:", mst)
    print("总权重:", total)
    # 手算期望：A-D(5) C-E(5) D-E(7) A-B(7) E-F(6) E-G(8) = 38
    print("与手算期望 38 对拍:", "✓" if total == 38 else "✗")


def demo_forest_vs_naive():
    print("=" * 60)
    print("21.4 路径压缩效果：链式 FIND 后树高塌缩")
    dsu = DisjointSetForest()
    # 造一条 1000 长的"链"（恶意用 UNION 小并大结束后再 FIND 全体）
    import random
    random.seed(1)
    n = 1000
    nodes = [dsu.make_set(i) for i in range(n)]
    # 顺序 union（0,1),(1,2)... 不带按秩会成链；这里演示按秩+压缩的综合效果
    for i in range(n - 1):
        dsu.union(nodes[i], nodes[i + 1])
    DisjointSetForest.find_count = 0
    for i in range(n):
        dsu.find_set(nodes[i])
    before = DisjointSetForest.find_count
    # 第二遍：路径压缩后应接近 n
    DisjointSetForest.find_count = 0
    for i in range(n):
        dsu.find_set(nodes[i])
    after = DisjointSetForest.find_count
    print(f"第一遍 FIND 总步数（压缩发生在遍中）: {before}")
    print(f"第二遍 FIND 总步数（压缩后）      : {after}  ≈ n={n}")
    print("路径压缩使后续操作几乎 O(1):", "✓" if after <= n * 2 else "再看")


def main():
    print("=" * 60)
    print("A) 21.2 链表表示")
    dl = DisjointSetLinkedList()
    s1 = dl.make_set("a")
    s2 = dl.make_set("b")
    s3 = dl.make_set("c")
    s1m = s1.head
    s2m = s2.head
    s3m = s3.head
    merged = dl.union(s1, s2)
    merged = dl.union(merged, s3)
    print("UNION {a} ∪ {b} ∪ {c} =", dl.members(merged))
    print("find_set(成员 b) = 集合头:", dl.find_set(s2m) is merged)

    demo_connected_components()
    demo_kruskal_cycle()
    demo_forest_vs_naive()


if __name__ == "__main__":
    main()
