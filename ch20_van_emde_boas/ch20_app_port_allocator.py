# -*- coding: utf-8 -*-
"""
第20章 应用：vEB 树做端口分配器
《算法导论（原书第3版）》CLRS ch20

真实场景：TCP 端口池管理（Linux 内核语义）、路由器 NAT 表、游戏服务器开房。
  allocate()      分配最小可用端口        = extract-min + insert 补洞语义
  allocate_at(x)  分配 ≥x 的最小空闲口    = SUCCESSOR 驱动（vEB 的主场！）
  release(x)      归还端口                = insert

对比对手：
  A) 朴素 bitmap：从 x 起线性探测——O(u) 最坏
  B) vEB：SUCCESSOR O(lg lg u)——u=2^16 时仅 4 层递归

对拍 + 高密度（空闲口稀少）计时。
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch20_veb_tree import VEBTree


# ============================================================
# A) 朴素 bitmap 端口池
# ============================================================
class NaivePortPool:
    def __init__(self, u):
        self.u = u
        self.used = [False] * u

    def allocate(self):
        for i in range(self.u):
            if not self.used[i]:
                self.used[i] = True
                return i
        return None                              # 池满

    def allocate_at(self, x):
        for i in range(max(x, 0), self.u):
            if not self.used[i]:
                self.used[i] = True
                return i
        return None

    def release(self, x):
        self.used[x] = False


# ============================================================
# B) vEB 端口池
# ============================================================
class VEBPortPool:
    def __init__(self, u):
        assert (u & (u - 1)) == 0 and u >= 2
        self.u = u
        self.tree = VEBTree(u)

    def allocate(self):
        """最小可用端口 = 树里最小的"空闲口"。上电时全空闲 → 0。"""
        m = self.tree.minimum()
        if m is None:
            return None
        self.tree.delete(m)
        return m

    def allocate_at(self, x):
        """≥x 的最小空闲口：SUCCESSOR(x-1) 驱动。O(lg lg u)。"""
        s = self.tree.successor(x - 1)
        if s is None:
            return None
        self.tree.delete(s)
        return s

    def release(self, x):
        if not self.tree.member(x):
            self.tree.insert(x)

    def is_free(self, x):
        return self.tree.member(x)


def port_app_init(pool, free_init):
    """初始化：free_init = 初始空闲集合。
    naive 的 used[x] 应为 True 当且仅当 x 不空闲。"""
    if isinstance(pool, VEBPortPool):
        for x in free_init:
            pool.tree.insert(x)
    else:
        for x in range(pool.u):
            pool.used[x] = x not in free_init


# ============================================================
# 对拍 + 计时
# ============================================================
def main():
    U = 1 << 16                     # 65536 口
    print("=" * 60)
    print(f"应用：端口池对拍（宇宙 u={U}）")

    # -- 正确性 fuzz：两池同操作序，结果必须一致 --
    random.seed(3)
    naive = NaivePortPool(U)
    veb = VEBPortPool(U)
    all_free = set(range(U))
    port_app_init(veb, all_free)   # vEB 树 = 空闲集合
    bad = 0
    for step in range(3000):
        op = random.random()
        if op < 0.45:                           # allocate
            a = naive.allocate()
            b = veb.allocate()
            if a != b:
                bad += 1
                if bad == 1:
                    print(f"  ✗ step{step} allocate: naive={a} vEB={b}")
        elif op < 0.75:                         # allocate_at
            x = random.randrange(U)
            a = naive.allocate_at(x)
            b = veb.allocate_at(x)
            if a != b:
                bad += 1
                if bad == 1:
                    print(f"  ✗ step{step} allocate_at({x}): naive={a} vEB={b}")
        else:                                   # release（可能重释 → 幂等验证）
            x = random.randrange(U)
            naive.release(x)
            veb.release(x)
        if step % 1000 == 0 and step:
            # 空闲集一致性抽查
            for _ in range(20):
                x = random.randrange(U)
                if naive.used[x] != (not veb.is_free(x)):
                    bad += 1
                    break
    print(f"  3000 次随机 allocate/allocate_at/release 对拍:",
          "✓ 全一致" if bad == 0 else f"✗ {bad} 次分歧")

    # -- 效率：高密度场景（池快满，空闲口稀少）--
    print("-" * 60)
    print("效率：池占用 99.5%（空闲口仅 327 个，散布在 65536 中）")
    random.seed(11)
    U = 1 << 16
    naive = NaivePortPool(U)
    veb = VEBPortPool(U)
    free = set(random.sample(range(U), 327))
    port_app_init(veb, free)
    port_app_init(naive, free)

    queries = [random.randrange(U) for _ in range(327)]
    t0 = time.perf_counter()
    r_naive = [naive.allocate_at(q) for q in queries]
    t_naive = time.perf_counter() - t0
    t0 = time.perf_counter()
    r_veb = [veb.allocate_at(q) for q in queries]
    t_veb = time.perf_counter() - t0
    same = r_naive == r_veb
    print(f"  327 次 allocate_at（每次分配直接耗掉一个空闲口）：结果一致 {'✓' if same else '✗'}")
    print(f"  朴素线性探测 O(u)    {t_naive*1000:9.2f} ms")
    print(f"  vEB SUCCESSOR O(lg lg u) {t_veb*1000:8.2f} ms → 快 {t_naive/t_veb:.1f} 倍")
    print("  读数：空闲越稀，朴素探测平均爬 ~u/2 步；vEB 恒 4 层递归（lg lg 65536=4）。")
    print("  纯 Python 递归仍有常数开销，但 u 增大趋势单调利于 vEB（渐进优势在 lg lg u）。")


if __name__ == "__main__":
    main()
