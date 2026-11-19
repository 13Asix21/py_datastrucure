# -*- coding: utf-8 -*-
"""
第11章 散列表 —— 11.1 直接寻址表
《算法导论（原书第3版）》CLRS

直接寻址表：关键字全域 U = {0,1,...,m-1}，一个长度 m 的数组,
槽位 k 直接就是下标 k —— insert/search/delete 全 O(1)。
缺点显而易见：全域太大时内存爆掉（比如 64 位手机号）。
散列表（11.2 起）就是为解决"全域大、实际存的关键字少"而生的。
"""


class DirectAddressTable:
    def __init__(self, universe_size):
        self.m = universe_size
        self.T = [None] * universe_size

    def direct_address_insert(self, x):
        """DIRECT-ADDRESS-INSERT(T, x)：T[x.key] = x"""
        if not (0 <= x.key < self.m):
            raise KeyError(f"key {x.key} 超出全域 [0, {self.m})")
        self.T[x.key] = x

    def direct_address_search(self, k):
        """DIRECT-ADDRESS-SEARCH(T, k)：return T[k]"""
        if not (0 <= k < self.m):
            return None
        return self.T[k]

    def direct_address_delete(self, x):
        """DIRECT-ADDRESS-DELETE(T, x)：T[x.key] = NIL"""
        self.T[x.key] = None


class SatelliteData:
    """除关键字外的其他数据（卫星数据）。"""
    __slots__ = ("key", "name", "score")

    def __init__(self, key, name, score):
        self.key = key
        self.name = name
        self.score = score

    def __repr__(self):
        return f"{self.key}:{self.name}/{self.score}"


def demo():
    print("=" * 60)
    print("11.1 直接寻址表：关键字即下标")
    # 场景：员工编号 0~99，全域 m=100
    T = DirectAddressTable(100)
    emps = [
        SatelliteData(7, "张三", 88),
        SatelliteData(23, "李四", 92),
        SatelliteData(99, "王五", 75),
    ]
    for e in emps:
        T.direct_address_insert(e)
    print("已插入:", emps)
    print("search(23):", T.direct_address_search(23))
    print("search(50):", T.direct_address_search(50), "（None = 无此人）")
    zhang = T.direct_address_search(7)
    T.direct_address_delete(zhang)
    print("delete 张三后再 search(7):", T.direct_address_search(7))
    print()
    print("为什么需要散列表？")
    print("  若关键字是 64 位整数，全域 = 2^64 ≈ 1.8e19 个槽位，")
    print("  实际只存 n=100 万个 key → 直接寻址要 2^64 空间，利用率 0.0000000000000053%。")
    print("  散列表用 m = Θ(n) 的空间 + 散列函数 h(k) 压缩映射，代价是可能碰撞。")


if __name__ == "__main__":
    demo()
