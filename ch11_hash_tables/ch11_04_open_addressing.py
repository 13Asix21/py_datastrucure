# -*- coding: utf-8 -*-
"""
第11章 散列表 —— 11.4 开放寻址法
《算法导论（原书第3版）》CLRS

探查序列：
  线性探查        h(k,i) = (h'(k) + i) mod m        —— 一次群集
  二次探查        h(k,i) = (h'(k) + c1·i + c2·i²) mod m —— 二次群集
  双重散列        h(k,i) = (h1(k) + i·h2(k)) mod m  —— 教科书推荐

开放寻址的删除用 DELETED 墓碑标记，不能直接置 NIL（会断探查链）。
α ≤ 1 必须成立；α 升高时探查代价急剧上升（α=0.5 尚可，0.9 崩坏）。
"""


DELETED = object()   # 墓碑标记
EMPTY = None         # 空槽


class OpenAddressingTable:
    """双重散列开放寻址表（附线性/二次探查可选）。槽数 m 取质数。"""

    def __init__(self, m=11, probe="double"):
        self.m = m
        self.T = [EMPTY] * m    # 存 (key, value)
        self.n = 0
        self.probe = probe
        self._special = 7       # h2 用的奇数参数

    # ---- 主/副散列 ----
    def h1(self, k):
        return k % self.m

    def h2(self, k):
        if self.probe == "double":
            # 副散列必须与 m 互素且不为 0，保证能探查整个表
            return 1 + (k % (self.m - 1))
        return 1

    def _probe_seq(self, k):
        """生成探查序列（生成器，最多 m 步）。"""
        h1v = self.h1(k)
        h2v = self.h2(k)
        for i in range(self.m):
            if self.probe == "linear":
                yield (h1v + i) % self.m
            elif self.probe == "quadratic":
                yield (h1v + 1 * i + 3 * i * i) % self.m
            else:  # double
                yield (h1v + i * h2v) % self.m

    # ---- 字典操作 ----
    def insert(self, key, value=0):
        """HASH-INSERT。α≤1 必须，α 大时代价急剧恶化。"""
        if self.n == self.m:
            raise OverflowError("表满：开放寻址 α 不可超过 1")
        for j in self._probe_seq(key):
            if self.T[j] is EMPTY or self.T[j] is DELETED:
                self.T[j] = (key, value)
                self.n += 1
                return j
        raise OverflowError(f"探查序列耗尽（m={self.m} 为合数时可能发生）")

    def search(self, key):
        """HASH-SEARCH：墓碑只跳过不断链。"""
        for j in self._probe_seq(key):
            slot = self.T[j]
            if slot is EMPTY:
                return None                    # 真空位 → key 不存在
            if slot is DELETED:
                continue                       # 墓碑：continue 探查
            if slot[0] == key:
                return (j, slot[1])
        return None

    def delete(self, key):
        for j in self._probe_seq(key):
            slot = self.T[j]
            if slot is EMPTY:
                return False
            if slot is not DELETED and slot[0] == key:
                self.T[j] = DELETED            # 关键：墓碑，不是 NIL！
                self.n -= 1
                return True
        return False

    def alpha(self):
        return self.n / self.m

    def snapshot(self):
        out = []
        for j, slot in enumerate(self.T):
            if slot is EMPTY:
                out.append("·")
            elif slot is DELETED:
                out.append("D")             # Deleted 墓碑
            else:
                out.append(str(slot[0]))
        return out


def demo_double_hashing():
    print("=" * 60)
    print("11.4 双重散列开放寻址（m=11 质数）")
    ht = OpenAddressingTable(m=11, probe="double")
    keys = [10, 22, 31, 4, 15, 28, 17, 88, 59]
    print("插入前表:", " ".join(ht.snapshot()))
    for k in keys:
        j = ht.insert(k)
        print(f"insert {k:3d} → 槽 {j:2d} | 表: {' '.join(ht.snapshot())}  α={ht.alpha():.2f}")
    print("search(59):", ht.search(59))
    print("delete(59) → 墓碑标记:", ht.delete(59))
    print("表:", " ".join(ht.snapshot()), "(D=墓碑)")
    print("search(59) 删除后:", ht.search(59))
    print("insert 相同位置的探查会复用墓碑槽:", ht.insert(59, "复用"), "→", " ".join(ht.snapshot()))


def demo_tombstone_and_search():
    print("=" * 60)
    print("墓碑的意义：delete 后 search 不能断链")
    ht = OpenAddressingTable(m=13, probe="double")
    k1, k2 = 20, 33          # h1: 20%13=7, 33%13=7 → 同起始槽，33 挤到下一个
    ht.insert(k1, "A"); ht.insert(k2, "B")
    print("insert 20, 33:", " ".join(ht.snapshot()))
    print("delete(20):", ht.delete(20))
    print("表（20 位置变墓碑 D）:", " ".join(ht.snapshot()))
    r = ht.search(33)
    print("search(33) 仍能找到 →", r, "✓ 若删成 NIL，33 就找不到了")
    # 若直接置 NIL
    bad = OpenAddressingTable(m=13, probe="double")
    bad.insert(k1, "A"); bad.insert(k2, "B")
    bad.T[7] = EMPTY
    print("反例（删成 NIL）search(33):", bad.search(33), "→ NIL 会断探查链 ✗")


def demo_probe_compare():
    print("=" * 60)
    print("线性 / 二次 / 双重 探查的群集对比")
    # 8 个 key 的 h1 全部相同（都 ≡ 0 mod 17），制造教科书式 primary clustering
    keys = [51, 68, 85, 102, 119, 136, 153, 170]
    for probe in ("linear", "quadratic", "double"):
        ht = OpenAddressingTable(m=17, probe=probe)
        for k in keys:
            ht.insert(k)
        snap = ht.snapshot()
        # 环形最长连续占用段（群集长度）
        max_run = run = 0
        for s in snap + snap[:1]:
            run = run + 1 if s != "·" else 0
            max_run = max(max_run, run)
        max_run = min(max_run, ht.m)
        print(f"  {probe:9s} → {' '.join(snap)}  最长群集: {max_run}")
    print("线性探查 → 8 个 key 排成一条直线长龙（一次群集，最长 8）；")
    print("二次探查 → 偏移量按 i² 增长，跳出线性长龙（最长 3）；")
    print("双重散列 → h2 随 key 变化；本批 key 的 h2 恰好线性递增（≈1 步长），")
    print("            结果呈'步进'分布——理论最优，但对特定 key 仍可能有结构。")


if __name__ == "__main__":
    demo_double_hashing()
    demo_tombstone_and_search()
    demo_probe_compare()
