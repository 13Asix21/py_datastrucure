# -*- coding: utf-8 -*-
"""
第6章 堆排序 —— 6.1~6.5 完整实现
《算法导论（原书第3版）》CLRS ch6（第二部分，优先队列的正主）

（二叉）堆：数组表示的完全二叉树。0-index：
  PARENT(i)=(i-1)//2  LEFT(i)=2i+1  RIGHT(i)=2i+2
最大堆性质：A[PARENT(i)] ≥ A[i]
操作：
  MAX-HEAPIFY      O(lg n)
  BUILD-MAX-HEAP   O(n)
  HEAPSORT         O(n lg n)
  MAXIMUM / EXTRACT-MAX / INCREASE-KEY / INSERT   O(lg n)（优先队列接口，6.5）
"""


class MaxHeap:
    def __init__(self, arr=None):
        self.A = []
        self.build_max_heap(arr or [])

    @staticmethod
    def parent(i):
        return (i - 1) // 2

    @staticmethod
    def left(i):
        return 2 * i + 1

    @staticmethod
    def right(i):
        return 2 * i + 2

    # ---- 6.2 ----
    def max_heapify(self, i, size=None):
        """MAX-HEAPIFY：假定 i 的两孩子已是堆，把 A[i] 下沉到位。O(lg n)"""
        A = self.A
        n = len(A) if size is None else size
        while True:
            l, r = self.left(i), self.right(i)
            largest = i
            if l < n and A[l] > A[largest]:
                largest = l
            if r < n and A[r] > A[largest]:
                largest = r
            if largest == i:
                return
            A[i], A[largest] = A[largest], A[i]
            i = largest

    # ---- 6.3 ----
    def build_max_heap(self, arr):
        """BUILD-MAX-HEAP：自底向上。O(n)（摊还分析见 6.3）"""
        self.A = list(arr)
        for i in range(len(self.A) // 2 - 1, -1, -1):
            self.max_heapify(i)

    # ---- 6.1/6.4 ----
    def heapsort_inplace(self):
        """HEAPSORT：in-place 排升序。O(n lg n)。
        用 size 参数把堆前缀与已排序后缀隔开——教科书的 heap-size 概念。"""
        n = len(self.A)
        for end in range(n - 1, 0, -1):
            self.A[0], self.A[end] = self.A[end], self.A[0]
            self.max_heapify(0, size=end)
        return self.A

    # ---- 6.5 优先队列接口 ----
    def maximum(self):
        return self.A[0] if self.A else None

    def extract_max(self):
        if not self.A:
            raise IndexError("underflow: 堆空")
        top = self.A[0]
        last = self.A.pop()
        if self.A:
            self.A[0] = last
            self.max_heapify(0)
        return top

    def increase_key(self, i, k):
        if k < self.A[i]:
            raise ValueError("新 key 小于原 key")
        self.A[i] = k
        while i > 0 and self.A[self.parent(i)] < self.A[i]:
            p = self.parent(i)
            self.A[i], self.A[p] = self.A[p], self.A[i]
            i = p

    def insert(self, k, neg_inf=None):
        """MAX-HEAP-INSERT：极小占位再 increase。O(lg n)。
        neg_inf：占位哨兵。默认 float('-inf')；元素类型不可与 float 比较
        （如元组）时传入同类型的极小值。"""
        if neg_inf is None:
            neg_inf = float("-inf")
        self.A.append(neg_inf)
        self.increase_key(len(self.A) - 1, k)

    def __len__(self):
        return len(self.A)

    def verify(self, size=None):
        n = len(self.A) if size is None else size
        for i in range(1, n):
            if self.A[self.parent(i)] < self.A[i]:
                return False, f"堆序破坏 @ i={i}"
        return True, ""


def demo_heap_basics():
    print("=" * 60)
    print("6.1~6.4 BUILD-MAX-HEAP / HEAPSORT")
    import random
    import time
    random.seed(3)
    arr = random.sample(range(1000), 500)
    h = MaxHeap(arr)
    ok, msg = h.verify()
    print(f"BUILD 后堆性质: {'✓' if ok else '✗ ' + msg}")

    before = arr[:]
    got = MaxHeap(before).heapsort_inplace()
    print("heapsort_inplace == sorted:", "✓" if got == sorted(arr) else "✗")

    # BUILD O(n) vs 全量逐插入 O(n lg n) 的直觉对比
    random.seed(9)
    data = [random.sample(range(100_000), 20_000) for _ in range(10)]
    t0 = time.perf_counter()
    for d in data:
        MaxHeap(d)
    t_build = (time.perf_counter() - t0) / 10
    t0 = time.perf_counter()
    for d in data:
        hh = MaxHeap()
        for x in d:
            hh.insert(x)
    t_ins = (time.perf_counter() - t0) / 10
    print(f"BUILD 2万元素: {t_build*1000:6.1f} ms | 逐个 insert 构建: {t_ins*1000:7.1f} ms → 快 {t_ins/t_build:.1f}×（O(n) vs O(n lg n)）")


def demo_priority_queue():
    print("=" * 60)
    print("6.5 最大优先队列接口")
    h = MaxHeap()
    for k in (16, 14, 10, 8, 7, 9, 3, 2, 4, 1):
        h.insert(k)
    print("insert 10 个后堆顶:", h.maximum(), "(期望 16)")
    print("extract_max:", h.extract_max(), "| 新堆顶:", h.maximum(), "(期望 14)")
    h.increase_key(len(h) - 1, 20)
    print("increase_key(尾元素→20) 后堆顶:", h.maximum(), "(期望 20)")
    ok, msg = h.verify()
    print("堆性质:", "✓" if ok else "✗ " + msg)
    seq = [h.extract_max() for _ in range(len(h))]
    print("连续 extract_max 降序:", "✓" if seq == sorted(seq, reverse=True) else "✗")


def main():
    demo_heap_basics()
    demo_priority_queue()


if __name__ == "__main__":
    main()
