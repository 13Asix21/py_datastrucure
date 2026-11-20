# -*- coding: utf-8 -*-
"""
串的模式匹配 —— 朴素算法 vs KMP
CLRS 第32章 字符串匹配（软考大纲："串的基本概念及模式匹配，简单匹配、KMP 思想"）

朴素匹配：O((n-m+1)·m) 最坏——文本全 a、模式 a...ab 时每趟对齐都几乎全程比对。
KMP：前缀函数 π（失败指针）+ 失配时模式向右滑动且比对成果不丢，O(n)。
  π[q] = P[0..q] 的最长相等真前后缀长度
  → 前缀函数的构建就是"模式对自身做匹配"（32.4 的精妙自反结构）

对拍：两种算法对 300 组随机串全一致（含最坏用例）；
     最坏用例实测字符比较数（教材最坏举证）。
"""

import random
import time


# ============================================================
# 32.1 朴素字符串匹配
# ============================================================
def naive_matcher(T, P, counter=None):
    """NAIVE-STRING-MATCHER。返回全部匹配起始位。"""
    n, m = len(T), len(P)
    out = []
    for s in range(n - m + 1):
        i = 0
        while i < m and T[s + i] == P[i]:
            if counter is not None:
                counter[0] += 1
            i += 1
        if counter is not None and i < m:
            counter[0] += 1                       # 失配那次也比较了
        if i == m:
            out.append(s)
    return out


# ============================================================
# 32.4 KMP
# ============================================================
def compute_prefix_function(P, counter=None):
    """COMPUTE-PREFIX-FUNCTION（教科书 32.4，1-based π）。O(m)。
    pi[q] = P[1..q] 的最长相等真前后缀长度（pi[0] 恒 0）。"""
    m = len(P)
    pi = [0] * m
    k = 0
    for q in range(1, m):
        while k > 0 and P[q] != P[k]:
            if counter is not None:
                counter[0] += 1
            k = pi[k - 1]
        if P[q] == P[k]:
            if counter is not None:
                counter[0] += 1
            k += 1
        pi[q] = k
    return pi


def kmp_matcher(T, P, counter=None):
    """KMP-MATCHER。返回全部匹配起始位。O(n)。"""
    n, m = len(T), len(P)
    if m == 0:
        return list(range(n + 1))
    pi = compute_prefix_function(P, counter)
    q = 0                                       # 已匹配的字符数
    outp = []
    for i in range(n):                          # 文本指针不回退！
        while q > 0 and T[i] != P[q]:
            if counter is not None:
                counter[0] += 1
            q = pi[q - 1]
        if T[i] == P[q]:
            if counter is not None:
                counter[0] += 1
            q += 1
        if q == m:
            outp.append(i - m + 1)
            q = pi[q - 1]                       # 继续找下一个
    return outp


# ============================================================
# demo
# ============================================================
def demo_correctness():
    print("=" * 60)
    print("朴素 vs KMP 正确性对拍（350 组随机 + 教科书样例 + 边界）")
    random.seed(3)
    cases = [
        ("abcabcabcabc", "abcab"),              # 教科书图 32-2 同款思想
        ("aabaabaaaabaab", "aabaa"),
        ("aaaaaaaaaa", "aaa"),
        ("hello", "hello"),
        ("hello", "world"),
        ("", "a"),
        ("a", ""),
    ]
    for _ in range(350):
        n = random.randrange(0, 60)
        m = random.randrange(0, min(n + 5, 10))
        T = "".join(random.choice("ab") for _ in range(n))
        P = "".join(random.choice("ab") for _ in range(m))
        cases.append((T, P))
    bad = 0
    for T, P in cases:
        a = naive_matcher(T, P)
        b = kmp_matcher(T, P)
        ref = [i for i in range(len(T) - len(P) + 1) if T[i:i + len(P)] == P] if P else list(range(len(T) + 1))
        if not (a == b == ref):
            bad += 1
            if bad <= 2:
                print(f"  ✗ T={T!r} P={P!r}: naive={a} kmp={b} ref={ref}")
    print(f"  {len(cases)} 组三方向:", "✓ 全部一致" if bad == 0 else f"✗ {bad} 组失败")


def demo_worst_case():
    print("=" * 60)
    print("最坏用例实测：T = 'a'*n + 'b'，P = 'a'*(m-1) + 'b'（每趟都对齐到底再失配）")
    n, m = 4000, 100
    T = "a" * n + "b"
    P = "a" * (m - 1) + "b"
    c1 = [0]
    naive_matcher(T, P, counter=c1)
    c2 = [0]
    kmp_matcher(T, P, counter=c2)
    print(f"  n={n}, m={m}:")
    print(f"  朴素比较次数 {c1[0]:>8} ≈ (n-m+1)·m 量级")
    print(f"  KMP  比较次数 {c2[0]:>8} ≈ n 量级 → 差 {c1[0]/max(c2[0],1):.0f}×")
    # 前缀函数可视化（教科书图 32-3 风格）
    P2 = "ababababca"
    pi = compute_prefix_function(P2)
    print(f"  示例 P='{P2}' 的 π 表: {pi}")
    print("  读数：π[q] 是『失配后模式滑动多少仍保持已比对成果』——KMP 从不回退文本指针，")
    print("        这是它 O(n+m) 的全部秘密；工程上（grep/BF）还要加坏字符/好后缀启发式（BM 系）。")


def demo_bench_real():
    print("=" * 60)
    print("真实规模计时：文本 500KB，随机模式 100 组")
    random.seed(11)
    n = 500_000
    T = "".join(random.choice("acgt") for _ in range(n))     # DNA 字母表
    t0 = time.perf_counter()
    for _ in range(100):
        i = random.randrange(n - 60)
        P = T[i:i + 40]
        kmp_matcher(T, P)
    t_kmp = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(5):                                       # 朴素慢，少测几组
        i = random.randrange(n - 60)
        P = T[i:i + 40]
        naive_matcher(T, P)
    t_naive = (time.perf_counter() - t0) / 5 * 100
    print(f"  100 次 KMP: {t_kmp*1000:.0f} ms | 100 次朴素(折算): {t_naive*1000:.0f} ms")
    print("  读数：随机文本+随机模式下朴素平均失配极早（~字母表大小），KMP 的收益全在最坏场景；上表 48× 才是它的主场。")
    print("        Python 的 str.find 是 C 版混合算法（BM 变体），生产代码直接用它。")
    t0 = time.perf_counter()
    for _ in range(100):
        i = random.randrange(n - 60)
        T.find(T[i:i + 40])
    t_builtin = time.perf_counter() - t0
    print(f"  参照：str.find 同任务 {t_builtin*1000:.0f} ms（C 实现的另一档常数）")


def main():
    demo_correctness()
    demo_worst_case()
    demo_bench_real()


if __name__ == "__main__":
    main()
