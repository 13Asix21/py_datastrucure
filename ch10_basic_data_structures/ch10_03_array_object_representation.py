# -*- coding: utf-8 -*-
"""
第10章 基本数据结构 —— 10.3 指针和对象的实现
《算法导论（原书第3版）》CLRS

问题：没有指针类型的语言，怎么实现链表和二叉树？
思路：用平行数组 key[] / next[] / prev[] 模拟对象，用空闲表（free list）
      管理"堆内存"，ALLOCATE-OBJECT / FREE-OBJECT 均 O(1)。

demo 内容：
  1) 多数组表示法 + 空闲表分配/释放（Figure 10.5~10.7 复现）
  2) 单数组表示法（对象字段 pack 进一个大数组，next 存相对基址）
"""


NULL = -1  # 用 -1 表示空指针（真实语言里是 NULL / None）


class MultiArrayObjectHeap:
    """多数组表示法：三个平行数组 + 空闲链。"""

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.key = [None] * capacity
        self.next = [NULL] * capacity
        self.prev = [NULL] * capacity
        self.head = NULL                       # 已用链表表头
        # 空闲链初始化：0 → 1 → 2 → ... → capacity-1 → NULL
        self.free = 0
        for i in range(capacity - 1):
            self.next[i] = i + 1
        self.next[capacity - 1] = NULL

    def allocate_object(self):
        """ALLOCATE-OBJECT：O(1)"""
        if self.free == NULL:
            raise OverflowError("object pool exhausted: 空闲表空")
        x = self.free
        self.free = self.next[x]
        return x

    def free_object(self, x):
        """FREE-OBJECT：O(1)，LIFO 复用"""
        self.next[x] = self.free
        self.prev[x] = NULL
        self.free = x

    def insert(self, k):
        """表头插入（LIST-INSERT'），元素来自空闲表。"""
        x = self.allocate_object()
        self.key[x] = k
        self.prev[x] = NULL
        self.next[x] = self.head
        if self.head != NULL:
            self.prev[self.head] = x
        self.head = x
        return x

    def delete(self, x):
        """把槽位 x 从已用链摘除并归还空闲表。"""
        if self.prev[x] != NULL:
            self.next[self.prev[x]] = self.next[x]
        else:
            self.head = self.next[x]
        if self.next[x] != NULL:
            self.prev[self.next[x]] = self.prev[x]
        self.free_object(x)

    def used_list(self):
        out, x = [], self.head
        while x != NULL:
            out.append((x, self.key[x]))
            x = self.next[x]
        return out

    def free_list(self):
        out, x = [], self.free
        while x != NULL:
            out.append(x)
            x = self.next[x]
        return out


def demo_multi_array():
    print("=" * 60)
    print("1) 多数组表示法：key/next/prev 平行数组 + 空闲表")
    h = MultiArrayObjectHeap(capacity=8)
    print("初始空闲链:", h.free_list())
    slots = []
    for k in (25, 4, 16, 9):
        s = h.insert(k)
        slots.append(s)
        print(f"insert {k:2d} → 占用槽位 {s} | 链表: {h.used_list()}")
    print(f"删除槽位 {slots[0]} (key={h.key[slots[0]]})")
    h.delete(slots[0])
    print("删后链表:", h.used_list())
    print("空闲链（可见刚归还的槽位在头部，LIFO 复用）:", h.free_list())
    reused = h.insert(100)
    print(f"再 insert 100 → 复用槽位 {reused}（== 刚释放的 {slots[0]}）| 链表: {h.used_list()}")


class SingleArrayObjectHeap:
    """单数组表示法：一个长数组里滚动 pack 对象的 3 个字段。

    对象 i 占 buf[3i..3i+2]：key / prev / next 存的是对象编号。
    """
    FIELDS = 3  # key, prev, next

    def __init__(self, capacity=6):
        self.cap = capacity
        self.buf = [None] * (capacity * self.FIELDS)
        self.head = None      # 表头对象编号
        self.free = 0         # 空闲链头对象编号
        for i in range(capacity - 1):
            self.buf[i * self.FIELDS + 2] = i + 1
        self.buf[self._base(capacity - 1) + 2] = None

    def _base(self, i):
        return i * self.FIELDS

    def allocate(self):
        if self.free is None:
            raise OverflowError("object pool exhausted")
        x = self.free
        self.free = self.buf[self._base(x) + 2]
        return x

    def release(self, x):
        self.buf[self._base(x) + 2] = self.free
        self.free = x

    def insert(self, k):
        x = self.allocate()
        b = self._base(x)
        self.buf[b] = k
        self.buf[b + 1] = None
        self.buf[b + 2] = self.head
        if self.head is not None:
            self.buf[self._base(self.head) + 1] = x
        self.head = x
        return x

    def delete(self, x):
        b = self._base(x)
        p, n = self.buf[b + 1], self.buf[b + 2]
        if p is not None:
            self.buf[self._base(p) + 2] = n
        else:
            self.head = n
        if n is not None:
            self.buf[self._base(n) + 1] = p
        self.release(x)

    def used_list(self):
        out, x = [], self.head
        while x is not None:
            b = self._base(x)
            out.append((x, self.buf[b]))
            x = self.buf[b + 2]
        return out


def demo_single_array():
    print("=" * 60)
    print("2) 单数组表示法：字段 pack 进一维数组，next 存对象编号")
    h = SingleArrayObjectHeap(capacity=6)
    slots = []
    for k in (25, 4, 16):
        s = h.insert(k)
        slots.append(s)
        print(f"insert {k:2d} → 对象#{s} (基址 {h._base(s)}) | 链表: {h.used_list()}")
    print(f"删除对象#{slots[1]} (key={h.buf[h._base(slots[1])]})")
    h.delete(slots[1])
    print("删后链表:", h.used_list())
    print("再 insert 42 复用刚才释放的对象槽 →", "对象#%d" % h.insert(42), "|", h.used_list())


if __name__ == "__main__":
    demo_multi_array()
    demo_single_array()
