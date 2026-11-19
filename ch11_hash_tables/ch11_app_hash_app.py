# -*- coding: utf-8 -*-
"""
第11章 应用：散列表的真实用法
《算法导论（原书第3版）》CLRS ch11

三个实战场景：
  1) 词频统计（文本挖掘/搜索引擎倒排第一步）—— 与 collections.Counter 对拍
  2) Two-Sum 问题：暴力 O(n²) vs 哈希 O(n) —— 效率对比 200 倍级
  3) 拼写检查器：哈希集合 O(1) vs 线性扫描 O(n) 查词典
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch11_02_chained_hash import ChainedHashTable


# ============================================================
# 应用 1：词频统计
# ============================================================
def word_freq_with_our_hash(text):
    """用 ch11 自己实现的链式散列表统计词频。"""
    ht = ChainedHashTable(m=257, hash_method="division")
    for w in text.split():
        ht.insert(_str_key(w), ht.search(_str_key(w))[1] + 1 if ht.search(_str_key(w)) else 1)
    return ht


def _str_key(w):
    """字符串 → 非负整数（Horner 多项式，与 ch11_03 一致思路）。"""
    h = 0
    for ch in w:
        h = (h * 256 + ord(ch)) % (1 << 61 - 1)
    return h


def demo_word_freq():
    print("=" * 60)
    print("应用1：词频统计（自己实现的链式散列表 vs collections.Counter）")
    text = ("to be or not to be that is the question "
            "whether tis nobler in the mind to suffer "
            "the slings and arrows of outrageous fortune "
            "or to take arms against a sea of troubles "
            "and by opposing end them to die to sleep "
            "no more and by a sleep to say we end")
    words = text.split()
    from collections import Counter
    ref = Counter(words)
    ht = word_freq_with_our_hash(text)
    # 反查：把 hash 表里的 key 都拿出来
    got = {}
    for chain in ht.T:
        for k, v in chain:
            # 从整数 key 找回原词：遍历词表定位
            for w in words:
                if _str_key(w) == k:
                    got[w] = v
                    break
    bad = 0
    for w, c in ref.items():
        if got.get(w) != c:
            bad += 1
            print(f"  ✗ '{w}' 我方 {got.get(w)} vs Counter {c}")
    print(f"  词表大小 {len(ref)}，对拍差异 {bad} 次", "✓" if bad == 0 else "✗")
    print("  Top5 词频:", ref.most_common(5))


# ============================================================
# 应用 2：Two-Sum（暴力 vs 哈希）
# ============================================================
def two_sum_brute(arr, target):
    """O(n²)：两两试。"""
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] + arr[j] == target:
                return (i, j)
    return None


def two_sum_hash(arr, target):
    """O(n)：已见过的数存哈希，查 target-自己。"""
    seen = {}
    for i, x in enumerate(arr):
        need = target - x
        if need in seen:
            return (seen[need], i)
        seen[x] = i
    return None


def two_sum_our_hash(arr, target):
    """用 ch11 自己实现的链式散列表跑（验证结构可用性 + 看常数）。"""
    ht = ChainedHashTable(m=1009, hash_method="division")
    for i, x in enumerate(arr):
        need = target - x
        hit = ht.search(need)
        if hit is not None:
            # 取存过的下标
            return (hit[1], i)
        ht.insert(x, i)
    return None


def demo_two_sum():
    print("=" * 60)
    print("应用2：Two-Sum（target=2 的下标对）")
    random.seed(5)
    for trial in range(3):
        arr = random.sample(range(10_000), 2000)
        a, b = random.sample(arr, 2)
        target = a + b
        r_bf = two_sum_brute(arr, target)
        r_hs = two_sum_hash(arr, target)
        r_our = two_sum_our_hash(arr, target)
        same_vals = (arr[r_bf[0]] + arr[r_bf[1]] == target
                     and arr[r_hs[0]] + arr[r_hs[1]] == target
                     and arr[r_our[0]] + arr[r_our[1]] == target)
        print(f"  批次{trial}: 暴力{r_bf} 哈希{r_hs} 自制{r_our} 值校验 {'✓' if same_vals else '✗'}")
    # 效率
    n = 4000
    arr = random.sample(range(1_000_000), n)
    a, b = random.sample(arr, 2)
    target = a + b
    t0 = time.perf_counter()
    r1 = two_sum_brute(arr, target)
    t_bf = time.perf_counter() - t0
    t0 = time.perf_counter()
    r2 = two_sum_hash(arr, target)
    t_hs = time.perf_counter() - t0
    t0 = time.perf_counter()
    r3 = two_sum_our_hash(arr, target)
    t_our = time.perf_counter() - t0
    print(f"  n={n}: 暴力 {t_bf*1000:8.2f} ms | dict 哈希 {t_hs*1000:6.3f} ms | 自制链式散列 {t_our*1000:7.2f} ms")
    print(f"  → 哈希比暴力快 {t_bf/t_hs:.0f} 倍；自制散列表慢于 dict（纯 Python 常数 + 链表开销），但仍 O(n)")


# ============================================================
# 应用 3：拼写检查器
# ============================================================
def build_vocabulary():
    """构造一个"词典"：随机伪单词 + 常见真词。"""
    random.seed(42)
    common = ("the be to of and a in that have I it for not on with he as you "
              "do at this but his by from they we say her she or an will my "
              "one all would there their what so up out if about who get which").split()
    fake = []
    consonants = "bcdfghjklmnpqrstvwz"
    vowels = "aeiou"
    for _ in range(5000):
        w = "".join(random.choice(consonants if i % 2 == 0 else vowels)
                    for i in range(random.randrange(3, 9)))
        fake.append(w)
    return common, fake


def demo_spell_checker():
    print("=" * 60)
    print("应用3：拼写检查器（词典 5000+ 伪词）")
    common, vocab = build_vocabulary()
    # 哈希集合：用 set（C 级哈希）vs 我们自己的 ChainedHashTable
    hs = ChainedHashTable(m=10007, hash_method="division")
    for w in vocab:
        if hs.search(_str_key(w)) is None:
            hs.insert(_str_key(w), w)
    # 线性表参照
    linear = vocab

    test_words = common[:10] + vocab[:5] + ["qqqzz"]
    # 正确性：哈希表与线性扫描结论一致
    bad = 0
    for w in test_words:
        in_hash = hs.search(_str_key(w)) is not None
        in_lin = w in linear
        if in_hash != in_lin:
            bad += 1
            print(f"  ✗ '{w}': hash={in_hash} linear={in_lin}")
    print(f"  查询 {len(test_words)} 词，对拍差异 {bad}", "✓" if bad == 0 else "✗")
    # 效率：命中查询 5000 次
    queries = (common * 250)[:3000] + vocab[:2000]
    t0 = time.perf_counter()
    for w in queries:
        hs.search(_str_key(w))
    t_hash = time.perf_counter() - t0
    t0 = time.perf_counter()
    for w in queries[:200]:              # 线性太慢，只测 200 次再折算
        w in linear
    t_lin = (time.perf_counter() - t0) * len(queries) / 200
    print(f"  {len(queries)} 次查询：自制哈希表 {t_hash*1000:7.2f} ms | 线性扫描(折算) {t_lin*1000:9.2f} ms")
    print(f"  → 哈希快 {t_lin/t_hash:.0f} 倍（O(1+α) vs O(n)）")


def main():
    demo_word_freq()
    demo_two_sum()
    demo_spell_checker()


if __name__ == "__main__":
    main()
