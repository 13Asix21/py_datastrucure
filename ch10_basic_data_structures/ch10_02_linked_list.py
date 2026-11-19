# -*- coding: utf-8 -*-
"""
第10章 基本数据结构 —— 10.2 链表
《算法导论（原书第3版）》CLRS

三种形态：
1. 单链表（无哨兵）
2. 双向链表（无哨兵）
3. 带哨兵的循环双向链表（教科书重点推荐）

核心对比：删除一个结点，单链表要 O(n) 找前驱；双向链表 O(1)；
哨兵把"边界判断"全部消掉，表头/表尾操作统一成纯指针搬运。
"""


class SingleListNode:
    __slots__ = ("key", "next")

    def __init__(self, key=None):
        self.key = key
        self.next = None


class DoublyListNode:
    __slots__ = ("key", "prev", "next")

    def __init__(self, key=None):
        self.key = key
        self.prev = None
        self.next = None


# ---------------------------------------------------------------
# 1. 单链表（无哨兵）
# ---------------------------------------------------------------
class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def insert_front(self, k):
        """表头插入 O(1)"""
        x = SingleListNode(k)
        x.next = self.head
        self.head = x

    def search(self, k):
        """O(n)"""
        x = self.head
        while x is not None and x.key != k:
            x = x.next
        return x

    def delete(self, x):
        """删除结点需先找前驱 → O(n)。这是单链表的硬伤。"""
        if x is None:
            raise ValueError("结点不存在")
        if x is self.head:
            self.head = x.next
            return
        prev = self.head
        while prev is not None and prev.next is not x:
            prev = prev.next
        if prev is None:
            raise ValueError("结点不在链表中")
        prev.next = x.next

    def to_list(self):
        out = []
        x = self.head
        while x is not None:
            out.append(x.key)
            x = x.next
        return out


# ---------------------------------------------------------------
# 2. 双向链表（无哨兵）
# ---------------------------------------------------------------
class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def insert_front(self, k):
        """O(1)"""
        x = DoublyListNode(k)
        x.next = self.head
        if self.head is not None:
            self.head.prev = x
        self.head = x

    def search(self, k):
        """O(n)"""
        x = self.head
        while x is not None and x.key != k:
            x = x.next
        return x

    def delete(self, x):
        """有 prev 指针，删除无需查找前驱 → O(1)。
        但仍要判断 x 是否为表头（边界），哨兵版连这个都省了。"""
        if x is None:
            raise ValueError("结点不存在")
        if x.prev is not None:
            x.prev.next = x.next
        else:
            self.head = x.next
        if x.next is not None:
            x.next.prev = x.prev

    def to_list(self):
        out = []
        x = self.head
        while x is not None:
            out.append(x.key)
            x = x.next
        return out


# ---------------------------------------------------------------
# 3. 带哨兵 nil 的循环双向链表（CLRS 10.2 主角）
# ---------------------------------------------------------------
class DoublyLinkedListWithSentinel:
    def __init__(self):
        self.nil = DoublyListNode()
        self.nil.prev = self.nil
        self.nil.next = self.nil

    def insert(self, k):
        """LIST-INSERT'：插到表头。全程无判空。O(1)"""
        x = DoublyListNode(k)
        x.next = self.nil.next
        self.nil.next.prev = x
        self.nil.next = x
        x.prev = self.nil
        return x

    def insert_tail(self, k):
        """插到表尾，同样是 O(1)、无判空。"""
        x = DoublyListNode(k)
        x.prev = self.nil.prev
        self.nil.prev.next = x
        self.nil.prev = x
        x.next = self.nil
        return x

    def delete(self, x):
        """LIST-DELETE'：O(1)，无任何边界判断。"""
        x.prev.next = x.next
        x.next.prev = x.prev

    def search(self, k):
        """LIST-SEARCH'：O(n)"""
        x = self.nil.next
        while x is not self.nil and x.key != k:
            x = x.next
        return None if x is self.nil else x

    def to_list(self):
        out = []
        x = self.nil.next
        while x is not self.nil:
            out.append(x.key)
            x = x.next
        return out


def demo():
    print("=" * 60)
    print("1) 单链表（无哨兵）")
    sl = SinglyLinkedList()
    for k in (4, 1, 9):
        sl.insert_front(k)
    print("insert_front 4,1,9  →", sl.to_list(), "（后插的在最前）")
    node9 = sl.search(9)
    print("search(9) 命中:", node9.key)
    sl.delete(node9)
    print("delete(9) →", sl.to_list())

    print("=" * 60)
    print("2) 双向链表（无哨兵）")
    dl = DoublyLinkedList()
    for k in (4, 1, 9):
        dl.insert_front(k)
    print("insert_front 4,1,9  →", dl.to_list())
    node1 = dl.search(1)
    dl.delete(node1)
    print("delete(1) →", dl.to_list(), "（O(1)，无需找前驱）")

    print("=" * 60)
    print("3) 带哨兵的循环双向链表")
    sen = DoublyLinkedListWithSentinel()
    sen.insert(9)
    sen.insert(16)
    sen.insert(4)
    sen.insert(25)
    print("insert(表头) 9,16,4,25 →", sen.to_list())
    sen.insert_tail(100)
    print("insert_tail(100) →", sen.to_list())
    x4 = sen.search(4)
    sen.delete(x4)
    x25 = sen.search(25)
    sen.delete(x25)
    print("delete 4 和 25 →", sen.to_list())
    print("空链表上操作也不崩：", end="")
    empty = DoublyLinkedListWithSentinel()
    empty.insert(1)
    print("insert(1) →", empty.to_list())


if __name__ == "__main__":
    demo()
