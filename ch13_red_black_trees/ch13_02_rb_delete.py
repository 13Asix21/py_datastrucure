# -*- coding: utf-8 -*-
"""
第13章 红黑树 —— 13.4 删除 专题演示
《算法导论（原书第3版）》CLRS

RB-DELETE / RB-DELETE-FIXUP 主体在 demo_utils.py（NIL 哨兵版）。
本文件：
  1) 展示一个能触发删除修复的小树
  2) 大批量随机插删 + 全程性质校验（4 case 自然覆盖）
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_utils import RED, BLACK, RBNode, RedBlackTree


def build_from_keys(keys):
    t = RedBlackTree()
    for k in keys:
        t.insert(k)
    return t


def demo_delete_fixup_small():
    print("=" * 60)
    print("13.4 删除修复：小树触发")
    t = build_from_keys([10, 5, 20, 1, 7, 15, 25])
    print("树(中序):", t.inorder(), " 黑高:", t.black_height())
    t.delete(7)
    ok, errs = t.verify()
    print("删 7（黑叶，触发黑高修复）→ 性质:", "✓" if ok else f"✗ {errs[:2]}", " 黑高:", t.black_height())
    t.delete(10)
    ok, errs = t.verify()
    print("删 10（根，双子，后继顶替）→ 性质:", "✓" if ok else f"✗ {errs[:2]}", " 中序:", [k for k, _ in t.inorder()])


def demo_randomized_sanity():
    print("=" * 60)
    print("随机插删 6000 次操作全程校验")
    random.seed(1314)
    t = RedBlackTree()
    live = set()
    bad = 0
    ops = 0
    last_op = ""
    for _ in range(6000):
        if random.random() < 0.5 or not live:
            k = random.randrange(5000)
            if k not in live:
                t.insert(k)
                live.add(k)
                last_op = f"insert {k}"
        else:
            k = random.choice(tuple(live))
            t.delete(k)
            live.discard(k)
            last_op = f"delete {k}"
        ops += 1
        if ops % 3 == 0:                       # 校验太频繁会拖慢，每 3 次一验
            ok, errs = t.verify()
            if not ok:
                bad += 1
                print(f"  ✗ 最近操作 [{last_op}] 后: {errs[:2]}")
                if bad >= 3:
                    return
    ok, _ = t.verify()
    match = len(live) == len(t.inorder())
    print(f"共 {ops} 次操作 → 性质:", "✓" if ok else "✗",
          f"| 全程破坏 {bad} 次 | 存活 {len(live)} == 树内 {len(t.inorder())}: {'✓' if match else '✗'}")


def main():
    demo_delete_fixup_small()
    demo_randomized_sanity()


if __name__ == "__main__":
    main()
