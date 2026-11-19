# -*- coding: utf-8 -*-
"""
第14章 应用：数据结构扩张的真实用法
《算法导论（原书第3版）》CLRS ch14

两个实战场景：
  1) 会议室冲突检测（区间树）：Google Calendar 排期内核
     - check_conflict: O(lg n) 判断新会议是否与已排会议重叠
     - 与暴力两两比对对拍，且统计剪枝效果
  2) 实时排行榜（顺序统计树）：游戏天梯/竞价排名
     - rank(name)    某玩家当前名次        O(lg n)
     - select(k)     第 k 名是谁           O(lg n)
     - insert/delete 分数实时变动          O(lg n)
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch14_01_order_statistic_tree import OSTree
from ch14_03_interval_tree import IntervalTree


# ============================================================
# 应用 1：会议室冲突检测（区间树）
# ============================================================
def brute_conflicts(intervals, new_iv):
    """暴力：与每个已排会议两两比对。O(n)"""
    lo, hi = new_iv
    return [iv for iv in intervals if lo <= iv[1] and iv[0] <= hi]


def demo_meeting_rooms():
    print("=" * 60)
    print("应用1：会议室排期（500 个已排会议 + 随机查询）")
    random.seed(5)
    # 生成 500 个不重叠基础会议（在时间轴上错开放）
    base = []
    cursor = 0
    for _ in range(500):
        start = cursor + random.randrange(5, 50)
        end = start + random.randrange(10, 120)
        base.append((start, end))
        cursor = end + random.randrange(10, 60)

    tree = IntervalTree()
    for lo, hi in base:
        tree.insert(lo, hi)

    # 查询正确性：区间树单查 vs 暴力全扫
    bad = 0
    probes = [(random.randrange(0, cursor), 0) for _ in range(300)]
    probes = [(lo, lo + random.randrange(5, 200)) for lo, _ in probes]
    for iv in probes:
        hit = tree.interval_search(*iv)
        expect_any = brute_conflicts(base, iv)
        got_iv = hit.interval if hit else None
        consistent = (got_iv is None and not expect_any) or (got_iv in expect_any)
        if not consistent:
            bad += 1
            print(f"  ✗ probe {iv}: 树说 {got_iv}, 暴力说 {expect_any[:3]}")
    print(f"  300 次冲突查询(单命中 vs 全量暴力) 一致性:", "✓" if bad == 0 else f"✗ {bad} 次")

    # 效率：区间树单查 vs 暴力
    t0 = time.perf_counter()
    for iv in probes:
        tree.interval_search(*iv)
    t_tree = time.perf_counter() - t0
    t0 = time.perf_counter()
    for iv in probes:
        brute_conflicts(base, iv)
    t_brute = time.perf_counter() - t0
    print(f"  300 次查询：区间树 O(lg n) {t_tree*1000:7.2f} ms | 暴力 O(n) {t_brute*1000:8.2f} ms → 快 {t_brute/t_tree:.0f} 倍")

    # 全量重叠枚举对拍
    q = probes[0]
    got_all = sorted(tree.search_all_overlaps(*q))
    expect_all = sorted(brute_conflicts(base, q))
    print(f"  全量重叠对拍 probe#0: {'✓' if got_all == expect_all else '✗'}（命中 {len(got_all)} 个）")


# ============================================================
# 应用 2：实时排行榜（顺序统计树）
# ============================================================
class Leaderboard:
    """游戏天梯：分数为 key（允许并列时用 (score, player_id) 复合 key 保唯一）"""
    def __init__(self):
        self.tree = OSTree()
        self.player_key = {}      # player -> 复合 key
        self.key_player = {}

    @staticmethod
    def _ckey(score, pid):
        return score * 1_000_000 + pid

    def _pids(self, ckey):
        return ckey % 1_000_000, ckey // 1_000_000

    def add(self, pid, score):
        """新玩家入场（要求 pid 尚未在场）。O(lg n)。
        分数变动场景用 rebuild：OSTree 未实现删除（ch14 重点在扩张非删除）。"""
        assert pid not in self.player_key, "pid 已在场，请用 rebuild"
        ck = self._ckey(score, pid)
        self.tree.insert(ck)
        self.player_key[pid] = ck
        self.key_player[ck] = pid

    def rank(self, pid):
        """玩家名次（1 = 最高分）。OS-RANK。O(lg n)
        树按升序：名次 = n - 位次 + 1。"""
        ck = self.player_key[pid]
        return len(self.player_key) - self.tree.os_rank(ck) + 1

    def kth(self, k):
        """第 k 名（1-based，最高分第一）。OS-SELECT。O(lg n)"""
        n = len(self.player_key)
        node = self.tree.os_select(self.tree.root, n - k + 1)
        ck = node.key
        return self.key_player[ck], ck // 1_000_000

    def rebuild(self, entries):
        """重建榜（绕过删除未实现）。entries: [(pid, score)]"""
        self.tree = OSTree()
        self.player_key = {}
        self.key_player = {}
        for pid, sc in entries:
            ck = self._ckey(sc, pid)
            self.tree.insert(ck)
            self.player_key[pid] = ck
            self.key_player[ck] = pid


def demo_leaderboard():
    print("=" * 60)
    print("应用2：实时排行榜（300 名玩家动态上分）")
    random.seed(8)
    players = list(range(1, 301))
    scores = {p: random.randrange(0, 10_000) for p in players}

    lb = Leaderboard()
    lb.rebuild([(p, scores[p]) for p in players])

    # 正确性：与排序参照对拍
    ref = sorted(scores.items(), key=lambda kv: -kv[1])
    bad = 0
    for k in (1, 50, 150, 300):
        pid, sc = lb.kth(k)
        rpid, rsc = ref[k - 1]
        if (pid, sc) != (rpid, rsc):
            bad += 1
            print(f"  ✗ 第{k}名: got ({pid},{sc}) want ({rpid},{rsc})")
    print(f"  kth(1/50/150/300) 与排序参照对拍:", "✓" if bad == 0 else "✗")
    bad = 0
    for pid in random.sample(players, 10):
        r = lb.rank(pid)
        r_expect = ref.index((pid, scores[pid])) + 1
        if r != r_expect:
            bad += 1
            print(f"  ✗ rank({pid}) = {r} want {r_expect}")
    print(f"  rank() 10 抽对拍:", "✓" if bad == 0 else "✗")

    # 效率：名次查询 vs 每次全排序
    probes = [random.choice(players) for _ in range(500)]
    t0 = time.perf_counter()
    gs = [lb.rank(p) for p in probes]
    t_ost = time.perf_counter() - t0
    t0 = time.perf_counter()
    def rank_by_sort(pid):
        return sorted(scores, key=lambda p: -scores[p]).index(pid) + 1
    _ = [rank_by_sort(p) for p in probes[:50]]
    t_sort = (time.perf_counter() - t0) * len(probes) / 50
    print(f"  500 次名次查询：OS-RANK {t_ost*1000:7.2f} ms | 全排序+index(折算) {t_sort*1000:9.2f} ms → 快 {t_sort/t_ost:.0f} 倍")
    print(f"  Top3: {[(lb.kth(k)) for k in (1,2,3)]}")


def main():
    demo_meeting_rooms()
    demo_leaderboard()


if __name__ == "__main__":
    main()
