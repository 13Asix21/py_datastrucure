# -*- coding: utf-8 -*-
"""
第11章 散列表 —— 11.3 散列函数
《算法导论（原书第3版）》CLRS

三大类：
1. 除法散列法 h(k) = k mod m —— m 别取 2 的幂
2. 乘法散列法 h(k) = floor(m·(kA mod 1)), A = (√5-1)/2 ≈ 0.618
3. 全域散列（universal hashing）—— 随机选 h，对抗恶意输入

字符串关键字的常规做法（思考题11.2 风格）：把字符串按 R 进制多项式求值后取模。
"""


import random


def h_division(k, m):
    """除法散列：m 取质数、远离 2 的幂。"""
    return k % m


def h_multiplication(k, m):
    """乘法散列：m 的选择不敏感，常取 2 的幂配合位运算。"""
    A = 0.6180339887498949   # (√5 - 1) / 2
    return int(m * ((k * A) % 1.0))


def h_string(s, m, R=256):
    """字符串 → 整数：以 R=256 为基的多项式散列（Horner 法）。"""
    hval = 0
    for ch in s:
        hval = (hval * R + ord(ch)) % m
    return hval


class UniversalHashFamily:
    """11.3.3 全域散列：h_{a,b}(k) = ((a·k + b) mod p) mod m
    从族 {h_ab} 中随机选一个来用，任何固定 key 序列的期望碰撞概率 ≤ 1/m。
    """
    def __init__(self, m, p=None):
        self.m = m
        # p 取大于全域上界的大质数（假定 key < 2^61）
        self.p = p if p is not None else (1 << 61) - 1  # Mersenne 质数 2^61-1
        self.a = random.randrange(1, self.p)
        self.b = random.randrange(0, self.p)

    def h(self, k):
        return ((self.a * k + self.b) % self.p) % self.m

    def re_randomize(self):
        """换一个散列函数（重建时用）。"""
        self.a = random.randrange(1, self.p)
        self.b = random.randrange(0, self.p)


def demo_division_vs_multiplication():
    print("=" * 60)
    print("1) 除法 vs 乘法 散列分布对比（同一批 key）")
    keys = [i * 8 for i in range(40)]  # 步长 8 的等差 key
    m = 16
    div = [h_division(k, m) for k in keys]
    mul = [h_multiplication(k, m) for k in keys]
    print(f"m={m}, key=0,8,16,...,312")
    print("除法 h(k)=k mod 16 → 分布:", [div.count(j) for j in range(m)])
    print(f"乘法 A=0.618        → 分布:", [mul.count(j) for j in range(m)])
    print("除法遇到 2 的幂 m + 步长 8 的 key：全部撞进 8 的倍数槽；乘法仍分散。")


def demo_string_hash():
    print("=" * 60)
    print("2) 字符串关键字的多项式散列（Horner 展开）")
    m = 37
    words = ["apple", "apply", "bbd", "helloworld", "str", "x"]
    for w in words:
        print(f'  h("{w}", m={m}) = {h_string(w, m)}')


def demo_universal():
    print("=" * 60)
    print("3) 全域散列：随机选 h 后，固定 key 的碰撞概率 ≤ 1/m")
    m = 16
    fam = UniversalHashFamily(m)
    keys = [random.randrange(100000) for _ in range(200)]
    slots = [fam.h(k) for k in keys]
    occupied = len(set(slots))
    print(f"200 个随机 key, m=16 → 占用槽位数 {occupied}/16")
    print("当前 h 的参数: a=%d..., b=%d (mod p=2^61-1)" % (fam.a % 10007, fam.b % 10007))
    # 碰撞率下界
    from collections import Counter
    cnt = Counter(slots).most_common(1)[0]
    print(f"最挤的槽: T[{cnt[0]}] 有 {cnt[1]} 个 key（期望 n/m = {200/m:.0f}）")


if __name__ == "__main__":
    random.seed(42)
    demo_division_vs_multiplication()
    demo_string_hash()
    demo_universal()
