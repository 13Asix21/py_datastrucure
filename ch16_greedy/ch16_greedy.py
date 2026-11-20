# -*- coding: utf-8 -*-
"""
第16章 贪心算法 —— 16.1 活动选择 / 16.3 哈夫曼编码
《算法导论（原书第3版）》CLRS ch16

贪心可行条件：贪心选择性质 + 最优子结构（16.2 的理论基础）。
  16.1 活动选择：按结束时间贪心，O(n lg n)
  16.3 哈夫曼编码：自底向上双队列合并，O(n lg n)

对拍：活动选择 vs DP 全解；哈夫曼编码 vs 等长/随机编码压缩率 + 最优性抽验。
"""

import heapq
import random


# ============================================================
# 16.1 活动选择
# ============================================================
def greedy_activity_selector(start, finish):
    """GREEDY-ACTIVITY-SELECTOR：finish 已升序。返回选中活动下标。O(n)"""
    n = len(start)
    selected = [0] if n else []
    k = 0                                    # 最近选中的结束时间标兵
    for m in range(1, n):
        if start[m] >= finish[k]:
            selected.append(m)
            k = m
    return selected


def dp_activity_selector(start, finish):
    """DP 参照（15 章风格）：c[i][j] = a_i 后到 a_j 前的最大兼容活动数。
    O(n³)，n ≤ 200 演示规模够用。"""
    n = len(start)
    # 加哑元：a_0 结束于 -inf（起点哨兵），a_{n+1} 开始于 +inf（终点哨兵）
    s = [float("-inf")] + list(start) + [float("inf")]
    f = [float("-inf")] + list(finish) + [float("inf")]
    # c[i][j]: 使用 a_i..a_j 之间（不含端点）
    N = n + 2
    c = [[0] * N for _ in range(N)]
    for L in range(2, N):                    # 区间长度
        for i in range(0, N - L):
            j = i + L
            best = 0
            for k in range(i + 1, j):
                if s[k] >= f[i] and f[k] <= s[j]:      # k 兼容于 i 和 j
                    cand = c[i][k] + c[k][j] + 1
                    best = max(best, cand)
            c[i][j] = best
    return c[0][N - 1]


def demo_activities():
    print("=" * 60)
    print("16.1 活动选择（教科书图 16.1，11 个活动）")
    start = [1, 3, 0, 5, 3, 5, 6, 8, 8, 2, 12]
    finish = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    n = len(start)
    # 按 finish 排序的索引（教科书已排序，顺序吻合）
    order = sorted(range(n), key=lambda i: finish[i])
    s = [start[i] for i in order]
    f = [finish[i] for i in order]
    g = greedy_activity_selector(s, f)
    d = dp_activity_selector(s[:], f[:])
    print(f"  贪心选择 {len(g)} 个活动（下标按 finish 排序后）: {[(s[i], f[i]) for i in g]}")
    print(f"  DP 全局最优数 = {d}", "✓ 贪心=最优" if len(g) == d else "✗")
    # fuzz
    rng = random.Random(7)
    bad = 0
    for _ in range(120):
        m = rng.randrange(1, 15)
        ss, ff = [], []
        for _ in range(m):
            a = rng.randrange(0, 40)
            b = a + rng.randrange(1, 12)
            ss.append(a)
            ff.append(b)
        order = sorted(range(m), key=lambda i: ff[i])
        s2 = [ss[i] for i in order]
        f2 = [ff[i] for i in order]
        gg = greedy_activity_selector(s2, f2)
        dd = dp_activity_selector(s2, f2)
        if len(gg) != dd:
            bad += 1
    print(f"  120 组随机 fuzz（贪心 vs DP）:", "✓" if bad == 0 else f"✗ {bad}")
    print("  读数：贪心 O(n) 完胜 DP O(n³)——前提是贪心选择性质成立（结束最早者总在某个最优解里）。")


# ============================================================
# 16.3 哈夫曼编码
# ============================================================
class HuffNode:
    __slots__ = ("freq", "ch", "left", "right")

    def __init__(self, freq, ch=None, left=None, right=None):
        self.freq = freq
        self.ch = ch
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def huffman(freqs):
    """HUFFMAN(C)：freqs = {字符: 频率}。返回根。O(n lg n)"""
    heap = [HuffNode(f, ch=c) for c, f in freqs.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        x = heapq.heappop(heap)
        y = heapq.heappop(heap)
        z = HuffNode(x.freq + y.freq, left=x, right=y)
        heapq.heappush(heap, z)
    return heap[0]


def huffman_codes(root):
    """从根走出每个字符的编码表。"""
    codes = {}
    def walk(node, prefix):
        if node.ch is not None:
            codes[node.ch] = prefix or "0"      # 单字符树根给 "0"
            return
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")
    walk(root, "")
    return codes


def demo_huffman():
    print("=" * 60)
    print("16.3 哈夫曼编码（教科书样例 a:45 b:13 c:12 d:16 e:9 f:5）")
    freqs = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
    root = huffman(dict(freqs))
    codes = huffman_codes(root)
    total_bits = sum(freqs[c] * len(codes[c]) for c in freqs)
    print(f"  编码: {codes}")
    print(f"  加权总位长 = {total_bits}（教科书 224）", "✓" if total_bits == 224 else "✗")
    # 与固定 3 位等长编码对比
    fixed_bits = 3 * sum(freqs.values())
    print(f"  等长 3 位编码: {fixed_bits} 位 → 哈夫曼省 {(1 - total_bits/fixed_bits)*100:.0f}%")

    # 真实文本压缩实验
    text = ("the quick brown fox jumps over the lazy dog " * 40 +
            "emento mori data structures and algorithms " * 30).lower()
    from collections import Counter
    cnt = Counter(text)
    root = huffman(dict(cnt))
    codes = huffman_codes(root)
    huff_bits = sum(cnt[c] * len(codes[c]) for c in cnt)
    import math
    fixed_len = math.ceil(math.log2(len(cnt)))
    fixed_bits = fixed_len * len(text)
    ascii_bits = 8 * len(text)
    # 最优性抽验：哈夫曼平均位长 ≥ 熵（信源编码定理），且任意交换两位编码不更优可由构造保证
    entropy = -sum(cnt[c]/len(text) * math.log2(cnt[c]/len(text)) for c in cnt)
    avg_huff = huff_bits / len(text)
    print(f"  真实文本（{len(text)} 字符，{len(cnt)} 种符号）:")
    print(f"    哈夫曼平均 {avg_huff:.2f} 位/符号 | 理论下界 H = {entropy:.2f} 位/符号（熵）")
    print(f"    vs 定长 {fixed_len} 位: 省 {(1 - avg_huff/fixed_len)*100:.0f}% | vs ASCII 8 位: 省 {(1 - avg_huff/8)*100:.0f}%")
    print(f"    哈夫曼 ≥ 熵 + 1 位定理: {avg_huff:.2f} ∈ [H, H+1) = [{entropy:.2f}, {entropy+1:.2f}):",
          "✓" if entropy <= avg_huff < entropy + 1 else "注意：抽验超界")
    # 前缀码校验：任何 codeword 不是另一个的前缀
    words = sorted(codes.values(), key=len)
    ok_prefix = all(not w2.startswith(w1)
                    for i, w1 in enumerate(words)
                    for w2 in words[i+1:])
    print(f"  前缀码（无歧义解码）校验:", "✓" if ok_prefix else "✗")
    # 解码回环校验
    encoded = "".join(codes[c] for c in text[:1000])
    # 解码
    rev = {v: k for k, v in codes.items()}
    decoded = []
    i = 0
    while i < len(encoded):
        for L in range(1, 40):
            chunk = encoded[i:i+L]
            if chunk in rev:
                decoded.append(rev[chunk])
                i += L
                break
    print(f"  编码→解码回环（前 1000 字符）:", "✓" if "".join(decoded) == text[:1000] else "✗")


def main():
    demo_activities()
    demo_huffman()


if __name__ == "__main__":
    main()
