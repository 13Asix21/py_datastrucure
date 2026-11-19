# -*- coding utf-8 -*-
"""
第11章 散列表 —— 11.2 散列表（链接法）
《算法导论（原书第3版）》CLRS
本文件实现：
1. 除法散列法 h(k) = k mod m
2. 乘法散列法 h(k) = floor(m * (k*A mod 1))，A≈0.618
3. 链接法解决碰撞：T[j] 是双向链表，rehash 自动扩容
"""


import random


class ChainedHashTable:
    """链接法散列表：slot 是一个链表（这里用 list 模拟，操作语义一致）。"""

    def __init__(self, m=8, hash_method="division"):
        self.m = m
        self.n = 0
        self.hash_method = hash_method
        self.T = [[] for _ in range(m)]

    # ---- 散列函数（11.3）----
    def h(self, k):
        if self.hash_method == "division":
            # m 取远离 2 的幂的质数效果最好
            return k % self.m
        elif self.hash_method == "multiplication":
            A = 0.6180339887  # 黄金分割常数 (√5-1)/2
            frac = (k * A) % 1.0
            return int(self.m * frac)
        else:
            raise ValueError(f"未知散列方法 {self.hash_method}")

    # ---- 字典操作 ----
    def insert(self, key, value=None):
        """CHAINED-HASH-INSERT(T, x)：插到链头，摊还 O(1)"""
        j = self.h(key)
        # 若 key 已存在则覆盖（Python dict 语义，教科书不讨论重复 key）
        for i, (k, _) in enumerate(self.T[j]):
            if k == key:
                self.T[j][i] = (key, value)
                return
        self.T[j].append((key, value))  # 实际应 insert(0,...) 到链头
        self.n += 1
        if self.n > self.m:             # 负载因子 α > 1 时 rehash
            self._rehash()

    def search(self, key):
        """CHAINED-HASH-SEARCH：O(1+α)"""
        j = self.h(key)
        for (k, v) in self.T[j]:
            if k == key:
                return (k, v)
        return None

    def delete(self, key):
        """CHAINED-HASH-DELETE"""
        j = self.h(key)
        for i, (k, _) in enumerate(self.T[j]):
            if k == key:
                del self.T[j][i]
                self.n -= 1
                return True
        return False

    def _rehash(self):
        old_items = [(k, v) for chain in self.T for (k, v) in chain]
        self.m *= 2
        # m 变成 2 的幂与除法散列不搭 → 找下一个质数
        self.m = _next_prime(self.m)
        self.T = [[] for _ in range(self.m)]
        self.n = 0
        for (k, v) in old_items:
            self._insert_no_rehash(k, v)

    def _insert_no_rehash(self, key, value):
        self.T[self.h(key)].append((key, value))
        self.n += 1

    def load_factor(self):
        return self.n / self.m

    def stats(self):
        lens = [len(c) for c in self.T]
        return f"m={self.m}, n={self.n}, α={self.load_factor():.2f}, 链长分布 {lens}"


def _next_prime(n):
    def is_prime(x):
        if x < 2:
            return False
        i = 2
        while i * i <= x:
            if x % i == 0:
                return False
            i += 1
        return True
    while not is_prime(n):
        n += 1
    return n


def demo_chaining():
    print("=" * 60)
    print("11.2 链接法散列表（除法散列 m=7）")
    ht = ChainedHashTable(m=7, hash_method="division")
    keys = [10, 22, 31, 4, 15, 28, 17, 88, 59]
    print("关键序列:", keys)
    print("散列值 h(k)=k mod 7:", [k % 7 for k in keys])
    for k in keys:
        ht.insert(k, f"v{k}")
    print("插入后:", ht.stats())
    print("各槽链表:")
    for j, chain in enumerate(ht.T):
        print(f"  T[{j}]: {[k for k, _ in chain]}")
    print("search(22):", ht.search(22))
    print("search(99):", ht.search(99))
    print("delete(31):", ht.delete(31), "→", ht.stats())
    print("delete(31) 再删:", ht.delete(31), "（已不存在 → False）")


def demo_multiplication_vs_power_of_2():
    print("=" * 60)
    print("m 是 2 的幂 vs 质数，h(k)=k mod m 的键分布对比")
    keys = list(range(0, 128, 8))  # 全是 8 的倍数（结构化 key）
    m_pow2, m_prime = 16, 17
    dist_pow2 = {j: 0 for j in range(m_pow2)}
    dist_prime = {j: 0 for j in range(m_prime)}
    for k in keys:
        dist_pow2[k % m_pow2] += 1
        dist_prime[k % m_prime] += 1
    used2 = sum(1 for v in dist_pow2.values() if v > 0)
    usedp = sum(1 for v in dist_prime.values() if v > 0)
    print(f"key = 0,8,16,...,120（共 {len(keys)} 个，全是 8 的倍数）")
    print(f"m={m_pow2} (2^4)   → 仅占用 {used2}/{m_pow2} 个槽: {sorted(j for j in dist_pow2 if dist_pow2[j])}（链长 {max(dist_pow2.values())} 全挤在偶数槽）")
    print(f"m={m_prime} (质数)  → 占用 {usedp}/{m_prime} 个槽, 最长链 {max(dist_prime.values())}")
    print("结论：key 与 m 有公因子时（如都是 2 的幂），除法散列严重聚集；质数 m 可避免")


if __name__ == "__main__":
    demo_chaining()
    demo_multiplication_vs_power_of_2()
