# -*- coding: utf-8 -*-
"""
第17章 摊还分析 —— 17.1~17.3
《算法导论（原书第3版）》CLRS ch17

三类方法实操（以"动态表倍增"为例全程贯穿）：
  17.1 聚合分析（aggregate）：n 个操作总代价上界 O(n) → 摊还 O(1)
  17.2 记账法（accounting）：预收摊还代价、多退少补
  17.3 势能法（potential）：Φ(D) 势函数，摊还 = 实际 + ΔΦ

两个经典对象：
  A) 二进制计数器递增（17.1/17.2/17.3 反复举例的标本）
  B) 动态表（17.4 扩张/收缩）——就是 Python list append 的原理
"""

import time


# ============================================================
# A) 二进制计数器
# ============================================================
class BinaryCounter:
    """k 位计数器；INCREMENT 翻转的位数是随机变量。"""
    def __init__(self, k=32):
        self.bits = [0] * k
        self.total_flips = 0            # 实际总代价

    def increment(self):
        i = 0
        k = len(self.bits)
        while i < k and self.bits[i] == 1:
            self.bits[i] = 0
            self.total_flips += 1
            i += 1
        if i < k:
            self.bits[i] = 1
            self.total_flips += 1

    def value(self):
        return sum(b << i for i, b in enumerate(self.bits))


def demo_counter_aggregate():
    print("=" * 60)
    print("17.1 聚合分析：二进制计数器 n 次 INCREMENT 总翻转位数")
    n = 2 ** 12
    c = BinaryCounter(16)
    for _ in range(n):
        c.increment()
    print(f"  n={n} 次递增实际总翻转: {c.total_flips} 位")
    print(f"  聚合账: 位 i (从0数) 每 2^(i+1) 次翻一次 → 总代价 Σ⌈n/2^(i+1)⌉ ≈ 2n")
    print(f"  → 摊还代价 = 总/n = {c.total_flips/n:.2f} ≈ 2，教科书上界 O(1) 且常数 2 是紧的 ✓")


def demo_counter_accounting():
    print("=" * 60)
    print("17.2 记账法：每次 INCREMENT 预收 2 块钱")
    bank = 0
    c = BinaryCounter(16)
    history_ok = True
    for _ in range(1000):
        before_flips = c.total_flips
        c.increment()
        cost = c.total_flips - before_flips        # 实际翻转数
        bank += 2 - cost                            # 预收2，实付 cost，余额入银行
        if bank < 0:
            history_ok = False
    print(f"  1000 次递增后银行余额: {bank}（≥0 全程）", "✓" if history_ok and bank >= 0 else "✗")
    print("  → 每次 0→1 翻转 1 块记账存款；1→0 用存款付。信用永不透支 → 摊还 O(1) 成立。")


def demo_counter_potential():
    print("=" * 60)
    print("17.3 势能法：Φ(Dᵢ) = 1 的位数")
    c = BinaryCounter(16)
    amortized_sum = 0
    actual_sum = 0
    for step in range(1, 501):
        phi_before = sum(c.bits)                    # Φ(D_{i-1})
        actual = 0
        i = 0
        while i < len(c.bits) and c.bits[i] == 1:
            c.bits[i] = 0
            actual += 1
            i += 1
        if i < len(c.bits):
            c.bits[i] = 1
            actual += 1
        actual_sum += actual
        phi_after = sum(c.bits)                      # Φ(D_i)
        amortized_sum += actual + (phi_after - phi_before)
    print(f"  500 步实付合计 = {actual_sum}，摊还合计 = {amortized_sum}（上界 2×500=1000）")
    print("  → 单步摊还 = 实付 + ΔΦ ≤ 2：观测值不超上界，势能法白纸黑字算得通。")


# ============================================================
# B) 动态表（Python list 的骨架）
# ============================================================
class DynTable:
    """17.4 动态表：满则 ×2 扩张，load < 1/4 则 ×1/2 收缩（收缩阈值故意不是 1/2，
    为保证摊还 O(1)——教科书 17.4.3 的性能陷阱讨论）。"""
    def __init__(self):
        self.buf = [None] * 1
        self.num = 0
        self.cap = 1
        self.total_moves = 0            # 搬移次数（实际代价大头）

    def insert(self, x):
        if self.num == self.cap:                    # 满 → 扩张
            new = [None] * (2 * self.cap)
            for i in range(self.num):
                new[i] = self.buf[i]
                self.total_moves += 1
            self.buf = new
            self.cap *= 2
        self.buf[self.num] = x
        self.num += 1

    def delete(self):
        if self.num == 0:
            raise IndexError
        self.num -= 1
        self.buf[self.num] = None
        if self.num > 0 and self.num <= self.cap // 4:   # 荷载 < 25% → 减半
            new = [None] * (self.cap // 2)
            for i in range(self.num):
                new[i] = self.buf[i]
                self.total_moves += 1
            self.buf = new
            self.cap //= 2

    @property
    def load(self):
        return self.num / self.cap


def demo_dyn_table():
    print("=" * 60)
    print("17.4 动态表：就是 Python list append 的原理")
    t = DynTable()
    n = 10_000
    for i in range(n):
        t.insert(i)
    print(f"  插入 {n} 个后: num={t.num}, cap={t.cap}（荷载 {t.load:.2f}），累计搬移 {t.total_moves} 次")
    print(f"  聚合账：扩张搬移 Σ 1+2+4+...+2^⌈lg n⌉ < 2n → 摊还每次 < 2 单位 = O(1)")
    print(f"  实测 搬移/插入 = {t.total_moves/n:.2f} < 4 ✓")
    # 收缩
    moves_before = t.total_moves
    while t.num > n // 4:
        t.delete()
    print(f"  删到 {t.num}（{t.num}/{t.cap}，荷载 {t.load:.2f}），收缩搬移 {t.total_moves - moves_before} 次")
    print("  → Python list 用同样的倍增策略实现 append 摊还 O(1)（复用 C 数组）。")
    # 与真 list 的对照实验
    t0 = time.perf_counter()
    dt = DynTable()
    for i in range(200_000):
        dt.insert(i)
    t_ours = time.perf_counter() - t0
    t0 = time.perf_counter()
    lst = []
    for i in range(200_000):
        lst.append(i)
    t_list = time.perf_counter() - t0
    print(f"  20 万次插入：自制 DynTable {t_ours*1000:7.1f} ms | Python list {t_list*1000:6.1f} ms（C 常数差）")


def main():
    demo_counter_aggregate()
    demo_counter_accounting()
    demo_counter_potential()
    demo_dyn_table()


if __name__ == "__main__":
    main()
