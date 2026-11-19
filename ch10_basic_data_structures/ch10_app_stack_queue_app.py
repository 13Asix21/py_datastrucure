# -*- coding: utf-8 -*-
"""
第10章 应用：栈 / 队列 / 链表的真实用法
《算法导论（原书第3版）》CLRS ch10

三个实战场景 + 效率对比：
  1) 括号匹配 + 逆波兰表达式求值（栈的经典应用，编译器/计算器内核原理）
  2) LRU 缓存（哈希表 + 双向链表，Redis/操作系统页置换的核心结构）
  3) 效率测试：手写链表队列 vs Python deque（ deque=双向链表+C加速 ）
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch10_01_stack_and_queue import Stack, CircularQueue


# ============================================================
# 应用 1：括号匹配 + 逆波兰表达式（RPN）求值
# ============================================================
def is_balanced(s: str) -> bool:
    """括号匹配：遇左括号 PUSH，遇右括号 POP 比对。O(n)"""
    pairs = {")": "(", "]": "[", "}": "{"}
    st = Stack()
    for ch in s:
        if ch in "([{":
            st.push(ch)
        elif ch in ")]}":
            if st.stack_empty():
                return False
            if st.pop() != pairs[ch]:
                return False
    return st.stack_empty()


def eval_rpn(tokens):
    """RPN 求值（LeetCode 150 经典题）：操作数入栈，运算符弹两个算一个。"""
    st = Stack()
    for t in tokens:
        if t in "+-*/":
            b = st.pop()
            a = st.pop()
            if t == "+":
                st.push(a + b)
            elif t == "-":
                st.push(a - b)
            elif t == "*":
                st.push(a * b)
            else:
                q = abs(a) // abs(b)          # 向零截断，同 C 语义
                st.push(q if (a < 0) == (b < 0) else -q)
        else:
            st.push(int(t))
    return st.pop()


def demo_parentheses_and_rpn():
    print("=" * 60)
    print("应用1：括号匹配 + RPN 求值")
    cases = [
        ("(a[b]{c})", True),
        ("(a[b)c]", False),
        ("{[()()]}", True),
        ("(((", False),
        ("", True),
    ]
    for s, want in cases:
        got = is_balanced(s)
        flag = "✓" if got == want else "✗"
        print(f"  '{s}' → {got} (期望 {want}) {flag}")
    # RPN：(2+3)*8/4 = 10
    rpn = ["2", "3", "+", "8", "*", "4", "/"]
    print("  RPN ['2','3','+','8','*','4','/'] =", eval_rpn(rpn), "(期望 10)")
    rpn2 = ["4", "13", "5", "/", "+"]         # 4 + 13/5 = 4 + 2 = 6
    print("  RPN ['4','13','5','/','+'] =", eval_rpn(rpn2), "(期望 6; 13/5 向零截断=2)")


# ============================================================
# 应用 2：LRU 缓存（哈希 + 双向链表）
# ============================================================
class LRUNode:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """capacity 容量 LRU：get/put 均 O(1)。

    结构（Redis/OS 页置换同款）：
      dict:  key → 链表结点     （O(1) 定位）
      双向链表+哨兵：MRU 侧在头，LRU 侧在尾
    """
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.nil = LRUNode()                    # 哨兵
        self.nil.prev = self.nil.next = self.nil

    def _unlink(self, n):
        n.prev.next = n.next
        n.next.prev = n.prev

    def _push_front(self, n):
        n.next = self.nil.next
        n.prev = self.nil
        self.nil.next.prev = n
        self.nil.next = n

    def get(self, key):
        n = self.map.get(key)
        if n is None:
            return None
        self._unlink(n)                          # 移到 MRU
        self._push_front(n)
        return n.value

    def put(self, key, value):
        n = self.map.get(key)
        if n is not None:
            n.value = value
            self._unlink(n)
            self._push_front(n)
            return
        if len(self.map) == self.cap:
            lru = self.nil.prev                  # 淘汰 LRU 尾
            self._unlink(lru)
            del self.map[lru.key]
        n = LRUNode(key, value)
        self.map[key] = n
        self._push_front(n)


def demo_lru():
    print("=" * 60)
    print("应用2：LRU 缓存（容量2，LeetCode 146 标准序列）")
    c = LRUCache(2)
    c.put(1, "A")
    c.put(2, "B")
    print("  get(1):", c.get(1), "(期望 A)")
    c.put(3, "C")                                # 淘汰 key=2（最久未用）
    print("  put(3,C) 后 get(2):", c.get(2), "(期望 None → 已被淘汰)")
    c.put(4, "D")                                # 淘汰 key=1
    print("  put(4,D) 后 get(1):", c.get(1), "(期望 None)")
    print("  get(3):", c.get(3), "(期望 C)")
    print("  get(4):", c.get(4), "(期望 D)")
    # 大压力正确性：与 OrderedDict 参照实现对拍
    from collections import OrderedDict
    import random
    random.seed(3)
    class RefLRU:
        def __init__(self, cap):
            self.cap = cap
            self.od = OrderedDict()
        def get(self, k):
            if k in self.od:
                self.od.move_to_end(k)
                return self.od[k]
            return None
        def put(self, k, v):
            if k in self.od:
                self.od.move_to_end(k)
                self.od[k] = v
                return
            if len(self.od) == self.cap:
                self.od.popitem(last=False)
            self.od[k] = v
    mine, ref = LRUCache(50), RefLRU(50)
    bad = 0
    for _ in range(20000):
        op = random.random()
        k = random.randrange(120)
        if op < 0.55:
            v = random.randrange(10000)
            mine.put(k, v)
            ref.put(k, v)
        else:
            if mine.get(k) != ref.get(k):
                bad += 1
    print(f"  20000 次随机 get/put 对拍 OrderedDict：{"✓ 全一致" if bad == 0 else f'✗ {bad} 次不一致'}")


# ============================================================
# 应用 3：效率测试 —— 循环队列 vs Python list 头部删除 vs deque
# ============================================================
class NaiveQueueList:
    """反例：用 list 当队列，出队 pop(0) 是 O(n) 全体搬移。"""
    def __init__(self):
        self.buf = []
    def enqueue(self, x):
        self.buf.append(x)
    def dequeue(self):
        return self.buf.pop(0)


def timed(fn, *args):
    t0 = time.perf_counter()
    r = fn(*args)
    return r, time.perf_counter() - t0


def bench_queue(queue_factory, n, tag):
    q = queue_factory()
    def run():
        for i in range(n):
            q.enqueue(i)
        for _ in range(n):
            q.dequeue()
    _, dt = timed(run)
    print(f"  {tag:<38} {dt*1000:9.2f} ms")
    return dt


def demo_queue_efficiency():
    print("=" * 60)
    print("应用3：队列效率对比（各 enqueue+dequeue 100000 次）")
    from collections import deque
    n = 100_000

    class DequeWrap:
        def __init__(self):
            self.d = deque()
        def enqueue(self, x):
            self.d.append(x)
        def dequeue(self):
            return self.d.popleft()

    t_naive = bench_queue(NaiveQueueList, n, "list 反例   (pop(0)=O(n))")
    t_ours = bench_queue(CircularQueue, n, "ch10 CircularQueue (环形数组)")
    t_deque = bench_queue(DequeWrap, n, "collections.deque  (C 实现)")

    print(f"  → 环形队列比 list 反例快 {t_naive/t_ours:.0f} 倍；deque 是工业级参照系")


def main():
    demo_parentheses_and_rpn()
    demo_lru()
    demo_queue_efficiency()


if __name__ == "__main__":
    main()
