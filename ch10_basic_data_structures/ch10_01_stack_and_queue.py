# -*- coding: utf-8 -*-
"""
第10章 基本数据结构 —— 10.1 栈和队列
《算法导论（原书第3版）》CLRS

与教科书一致：用数组实现。
栈：LIFO，S.top 指向最新压入元素；PUSH/POP/STACK-EMPTY 均 O(1) 摊还。
队列：FIFO，Q.head 出队、Q.tail 入队，环绕式（circular）复用空间。
"""


class Stack:
    """10.1 栈。数组 + top 指针。"""

    def __init__(self, capacity=16):
        self._buf = [None] * capacity
        self.top = -1  # 栈顶下标，-1 表示空

    def stack_empty(self) -> bool:
        """STACK-EMPTY"""
        return self.top == -1

    def push(self, x) -> None:
        """PUSH：摊还 O(1)"""
        self.top += 1
        if self.top == len(self._buf):          # 溢出则倍增（摊还分析见17章）
            self._buf.extend([None] * len(self._buf))
        self._buf[self.top] = x

    def pop(self):
        """POP：O(1)"""
        if self.stack_empty():
            raise IndexError("underflow: 栈已空")
        x = self._buf[self.top]
        self._buf[self.top] = None             # 防滞留引用，教科书无此步
        self.top -= 1
        return x

    def __len__(self):
        return self.top + 1


class CircularQueue:
    """10.1 队列。Q.head 出队、Q.tail 入队，尾指针环绕。"""

    def __init__(self, capacity=16):
        self._buf = [None] * capacity
        self.head = 0    # 指向队头（下一个出队位置）
        self.tail = 0    # 指向队尾（下一个入队位置）
        self._count = 0  # 用计数区分“满”与“空”，避免留空位判断

    def enqueue(self, x) -> None:
        """ENQUEUE：摊还 O(1)"""
        if self._count == len(self._buf):
            self._grow()
        self._buf[self.tail] = x
        self.tail = (self.tail + 1) % len(self._buf)
        self._count += 1

    def dequeue(self):
        """DEQUEUE：O(1)"""
        if self._count == 0:
            raise IndexError("underflow: 队列已空")
        x = self._buf[self.head]
        self._buf[self.head] = None
        self.head = (self.head + 1) % len(self._buf)
        self._count -= 1
        return x

    def _grow(self):
        old = [self._buf[(self.head + i) % len(self._buf)]
               for i in range(self._count)]
        self._buf = old + [None] * (len(old) if len(old) else 4)
        self.head = 0
        self.tail = self._count

    def __len__(self):
        return self._count


def demo_stack():
    print("=" * 60)
    print("10.1 栈（LIFO）  —— PUSH 15,6,2,9 后连续 POP")
    s = Stack()
    print("初始为空?", s.stack_empty())
    for k in (15, 6, 2, 9):
        s.push(k)
    print("PUSH 15,6,2,9 →", f"top={s.top}, size={len(s)}")
    print("POP:", s.pop())
    print("POP:", s.pop())
    print("POP:", s.pop())
    print("POP:", s.pop())
    try:
        s.pop()
    except IndexError as e:
        print("POP 空栈 → IndexError:", e)


def demo_queue():
    print("=" * 60)
    print("10.1 队列（FIFO） —— 教科书配图：15,6,9,8 入队后处理")
    q = CircularQueue(capacity=4)
    for k in (15, 6, 9, 8):
        q.enqueue(k)
    print("ENQUEUE 15,6,9,8 →", f"head={q.head}, tail={q.tail}, size={len(q)}")
    print("DEQUEUE:", q.dequeue(), "← 队头 15 先出（FIFO）")
    print("DEQUEUE:", q.dequeue())
    print("满队时再入 4,17 → 触发扩容（环绕调整）")
    q.enqueue(4)
    q.enqueue(17)
    for _ in range(3):
        print("DEQUEUE:", q.dequeue())
    try:
        q.dequeue()
    except IndexError as e:
        print("DEQUEUE 空队 → IndexError:", e)


if __name__ == "__main__":
    demo_stack()
    demo_queue()
