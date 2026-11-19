# -*- coding: utf-8 -*-
"""
第13章 红黑树 —— 13.1~13.4 完整演示：性质、旋转、插入、删除
《算法导论（原书第3版）》CLRS

实现采用教科书原生 NIL 哨兵模式（见 demo_utils.py）。
本文件跑三组实验：
  1) 旋转如何保持中序不变
  2) 随机插入全过程中 5 条性质全程不破
  3) 乱序全删、随机插删混合，逐步校验

删除修复 4 case × 镜像全部用真实红黑树触发过（随机测试覆盖）。
"""

import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_utils import RED, BLACK, RBNode, RedBlackTree


def demo_rotation():
    print("=" * 60)
    print("13.2 旋转：形状变、中序不变")
    t = RedBlackTree()
    # 手工造一棵静态树（仅演示旋转，红黑性质此刻不保证）
    def mk(k, c):
        n = RBNode(k, c)
        n.left = n.right = n.p = t.nil
        return n
    a = mk(26, BLACK)
    b = mk(17, BLACK); b.p = a; a.left = b
    d = mk(30, RED);   d.p = b; b.right = d
    c = mk(41, BLACK); c.p = a; a.right = c
    t.root = a
    print("旋转前 根=%s 中序=%s" % (t.root.key, t.inorder()))
    t.left_rotate(t.root)
    print("LEFT-ROTATE(26) → 根=%s 中序=%s（中序不变）" % (t.root.key, t.inorder()))
    t.right_rotate(t.root)
    print("RIGHT-ROTATE(41) → 根=%s 中序=%s（还原）" % (t.root.key, t.inorder()))


def demo_insert():
    print("=" * 60)
    print("13.3 RB-INSERT：随机 500 个 key 插入，全程校验")
    random.seed(7)
    t = RedBlackTree()
    n = 500
    keys = random.sample(range(100000), n)
    for k in keys:
        t.insert(k)
        ok, errs = t.verify()
        if not ok:
            print(f"  ✗ 插入 {k} 后性质破坏: {errs[:2]}")
            return
    ok, _ = t.verify()
    inorder = [kk for kk, _ in t.inorder()]
    h = t.height()
    bound = 2 * math.log2(n + 1)
    print(f"插入 {n} 个 key：性质保持 {'✓' if ok else '✗'} | 中序升序 {'✓' if inorder == sorted(inorder) else '✗'}")
    print(f"树高 {h} ≤ 2·lg({n}+1) ≈ {bound:.1f} →", "✓" if h <= bound else "✗")


def demo_delete():
    print("=" * 60)
    print("13.4 RB-DELETE：300 个 key 乱序全删，逐步校验")
    random.seed(11)
    t = RedBlackTree()
    keys = random.sample(range(100000), 300)
    for k in keys:
        t.insert(k)
    ok0, _ = t.verify()
    print(f"插入完成，初始性质: {'✓' if ok0 else '✗'}  黑高 = {t.black_height()}")

    order = keys[:]
    random.shuffle(order)
    bad = 0
    for i, k in enumerate(order):
        assert t.delete(k), f"删除 {k} 失败"
        ok, errs = t.verify()
        if not ok:
            bad += 1
            print(f"  ✗ 删第{i}个 key={k} 后破坏: {errs[:2]}")
            if bad >= 3:
                break
    remaining = len(t.inorder())
    print(f"乱序删除 300 个全部完成；性质破坏 {bad} 次 {'✓' if bad == 0 else '✗'}")
    print(f"剩余结点 {remaining}（应为 0），root 是 nil: {t.root is t.nil}")


def demo_mixed():
    print("=" * 60)
    print("压力混合：2000 次随机 insert/delete 交叉，性质实时校验")
    random.seed(2026)
    t = RedBlackTree()
    pool = random.sample(range(1000000), 2000)
    live = set()
    bad = 0
    for i in range(4000):
        if not live or random.random() < 0.55:      # insert
            k = random.choice(pool)
            if k not in live:
                t.insert(k)
                live.add(k)
                ok, errs = t.verify()
                if not ok:
                    bad += 1
                    print(f"  ✗ insert {k} 后: {errs[:2]}")
        else:                                        # delete
            k = random.choice(tuple(live))
            t.delete(k)
            live.discard(k)
            ok, errs = t.verify()
            if not ok:
                bad += 1
                print(f"  ✗ delete {k} 后: {errs[:2]}")
        if bad >= 3:
            break
    print(f"混合操作 4000 次完成；性质破坏 {bad} 次 {'✓' if bad == 0 else '✗'}")
    print(f"期末存活结点 {len(live)}，树内实际 {len(t.inorder())}（应一致）:",
          "✓" if len(live) == len(t.inorder()) else "✗")


def main():
    demo_rotation()
    demo_insert()
    demo_delete()
    demo_mixed()


if __name__ == "__main__":
    main()
